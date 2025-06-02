import math

from django.db.models import Q, Case, When, Value, IntegerField
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

from app.base.pagination import CustomPagination
from app.core.utils.string import slugify, tokenize
from app.location import serializers
from app.location.models import Location, LocationType


DEFAULT_CACHE_TIME = 60 * 60 * 24
LARGE_NUMBER = 999999


class LocationModelViewSet(ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = serializers.LocationSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        search_query = self.request.query_params.get("search", None)
        location_type = self.request.query_params.get("type", None)
        province = self.request.query_params.get("province", None)
        city = self.request.query_params.get("city", None)
        district = self.request.query_params.get("district", None)
        ward = self.request.query_params.get("ward", None)

        queryset = super().get_queryset()
        queryset = queryset.filter(is_enabled=True)

        queryset = queryset.annotate(
            custom_order=Case(
                When(order=0, then=Value(LARGE_NUMBER)),
                default="order",
                output_field=IntegerField(),
            )
        ).order_by("custom_order", "name")

        if location_type:
            queryset = queryset.filter(type=location_type)

        if province:
            queryset = queryset.filter(province=slugify(province))

        if city:
            queryset = queryset.filter(city=slugify(city))

        if district:
            queryset = queryset.filter(district=slugify(district))

        if ward:
            queryset = queryset.filter(ward=slugify(ward))

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query)
                | Q(code__icontains=search_query)
                | Q(address__icontains=search_query)
                | Q(province__icontains=search_query)
                | Q(city__icontains=search_query)
                | Q(district__icontains=search_query)
                | Q(ward__icontains=search_query)
            )

        return queryset

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ["list", "retrieve"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        _list_action = lambda req, *a, **k: super(LocationModelViewSet, self).list(
            req, *a, **k
        )

        if request.query_params.get("search", None):
            return _list_action(request, *args, **kwargs)
        else:
            cached_list_view = cache_page(DEFAULT_CACHE_TIME)(_list_action)
            return cached_list_view(request, *args, **kwargs)

    @method_decorator(cache_page(DEFAULT_CACHE_TIME))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class OpenStreetMapSearchAPIView(APIView):
    DEFAULT_OSM_RESULTS_LIMIT = 50
    DEFAULT_PER_PAGE = 10

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        search_param, province_param = self._get_search_query(request.query_params)
        page, per_page = self._get_pagination(request.query_params)

        osm_query = self._build_osm_query(search_param, province_param)
        osm_locations = self._get_osm_locations(osm_query)
        transformed_results = self._transform_osm_locations(osm_locations)

        total_items = len(transformed_results)
        total_pages = math.ceil(total_items / per_page) if per_page > 0 else 0
        if page > total_pages and total_pages > 0:
            page = total_pages

        start_index = (page - 1) * per_page
        end_index = start_index + per_page
        paginated_osm_results = transformed_results[start_index:end_index]

        return Response(
            {
                "total": total_items,
                "total_page": total_pages,
                "per_page": per_page,
                "page": page,
                "results": paginated_osm_results,
            }
        )

    def _get_search_query(self, query_params):
        search_param = query_params.get("search", None)
        province_param = query_params.get("province", None)

        if not search_param:
            raise ValueError("Search query (search) is required.")

        return (
            search_param,
            province_param,
        )

    def _get_pagination(self, query_params):
        try:
            page = int(query_params.get("page", 1))
            per_page = int(query_params.get("per_page", self.DEFAULT_PER_PAGE))
        except ValueError:
            raise ValueError("Invalid page or per_page parameter.")

        if page < 1:
            page = 1
        if per_page < 1:
            per_page = self.DEFAULT_PER_PAGE

        return (
            page,
            per_page,
        )

    def _extract_address_component(self, osm_address_dict, component_keys):
        if not osm_address_dict or not isinstance(osm_address_dict, dict):
            return None
        for key in component_keys:
            if osm_address_dict.get(key):
                return osm_address_dict[key]
        return None

    def _get_location_type(self, osm_loc):
        location_type = LocationType.OTHER
        if osm_loc.raw.get("type") == "airport":
            location_type = LocationType.AIRPORT
        elif osm_loc.raw.get("type") == "hotel":
            location_type = LocationType.HOTEL
        elif osm_loc.raw.get("type") == "restaurant":
            location_type = LocationType.RESTAURANT
        return location_type

    def _get_latitude(self, osm_loc):
        return str(osm_loc.latitude) if osm_loc.latitude is not None else None

    def _get_longitude(self, osm_loc):
        return str(osm_loc.longitude) if osm_loc.longitude is not None else None

    def _build_osm_query(self, search_param, province_param):
        tokens = [
            *tokenize(search_param),
            *tokenize(province_param),
        ]
        return " ".join(tokens)

    def _get_osm_locations(self, osm_query):
        geolocator = Nominatim(user_agent="eskept_backend_app/1.0 osm_search")

        osm_locations = []

        try:
            raw_osm_locations = geolocator.geocode(
                osm_query,
                country_codes=["vn"],
                exactly_one=False,
                limit=self.DEFAULT_OSM_RESULTS_LIMIT,
                addressdetails=True,
            )
            if raw_osm_locations:
                osm_locations = (
                    raw_osm_locations
                    if isinstance(raw_osm_locations, list)
                    else [raw_osm_locations]
                )
            return osm_locations
        except GeocoderTimedOut:
            raise GeocoderTimedOut("Geocoding service timed out.")
        except GeocoderUnavailable:
            raise GeocoderUnavailable("Geocoding service unavailable.")
        except Exception:
            raise Exception("An unexpected error occurred during geocoding.")

    def _transform_osm_locations(self, osm_locations):
        transformed_results = []
        for osm_loc in osm_locations:
            if not osm_loc or not osm_loc.raw:
                continue

            raw_address = osm_loc.raw.get("address", {})

            name_parts = osm_loc.raw.get("display_name", "").split(",")
            extracted_name = (
                name_parts[0].strip() if name_parts else osm_loc.raw.get("display_name")
            )
            location_type = self._get_location_type(osm_loc)
            province = self._extract_address_component(
                raw_address, ["state", "province", "state_district"]
            )
            city = self._extract_address_component(
                raw_address, ["city", "town", "municipality", "county"]
            )
            district = self._extract_address_component(
                raw_address, ["suburb", "city_district", "district"]
            )
            ward = self._extract_address_component(
                raw_address, ["quarter", "neighbourhood", "ward"]
            )
            latitude = self._get_latitude(osm_loc)
            longitude = self._get_longitude(osm_loc)

            transformed_results.append(
                {
                    "id": f"osm_{osm_loc.raw.get('osm_id')}",
                    "created_at": None,
                    "updated_at": None,
                    "name": extracted_name,
                    "code": None,
                    "type": location_type,
                    "order": 0,
                    "is_enabled": True,
                    "address": osm_loc.raw.get("display_name"),
                    "province": province,
                    "city": city,
                    "district": district,
                    "ward": ward,
                    "latitude": latitude,
                    "longitude": longitude,
                }
            )

        return transformed_results
