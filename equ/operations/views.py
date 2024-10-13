import datetime
from operations.models import Operation, OperationType


# Create your views here.


def create_operation_log(request, operation_type, equipment,
                         location_old, location_new,
                         responsible_old, responsible_new):
    Operation(operation_type=OperationType.objects.get(pk=operation_type),
              date=datetime.datetime.now(),
              user=request.user,
              equipment=equipment,
              location_old=location_old,
              location_new=location_new,
              responsible_old=responsible_old,
              responsible_new=responsible_new).save()
