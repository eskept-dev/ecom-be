from rest_framework import serializers


class ViewProductAvailabilityRequestSerializer(serializers.Serializer):
    product_ids = serializers.ListField(child=serializers.IntegerField(), required=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)


class ViewProductAvailabilityItemResponseSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    booking_count = serializers.IntegerField()
    max_capacity = serializers.IntegerField()


class ViewProductAvailabilityResponseSerializer(serializers.Serializer):
    day = serializers.DateField()
    items = ViewProductAvailabilityItemResponseSerializer(many=True)
