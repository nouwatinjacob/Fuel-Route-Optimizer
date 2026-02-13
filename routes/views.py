from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from routes.models import FuelStation

from routes.serializers import RouteRequestSerializer
from routes.services.routing import RoutingService
from routes.services.fuel_optimizer import FuelOptimizer


class RouteAPIView(APIView):

    def post(self, request):
        serializer = RouteRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        routing_service = RoutingService()
        optimizer = FuelOptimizer()

        route = routing_service.get_route(
            data["start_city"],
            data["start_state"],
            data["end_city"],
            data["end_state"],
        )

        result = optimizer.optimize(route)

        return Response(result, status=status.HTTP_200_OK)
    
    

@require_http_methods(["GET"])
def health_check(request):
    try:
        station_count = FuelStation.objects.count()

        return JsonResponse({
            "status": "ok",
            "stations_loaded": station_count
        })
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)
