from datetime import datetime

from rest_framework import serializers


class FlexibleDateField(serializers.DateField):
    def to_internal_value(self, value):
        if isinstance(value, str):
            try:
                # Try standard date parsing first
                return super().to_internal_value(value)
            except serializers.ValidationError:
                # Try parsing as ISO datetime and extract date
                try:
                    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    return dt.date()
                except Exception:
                    pass
        self.fail('invalid', format='YYYY-MM-DD or ISO 8601 datetime')