import datetime
from operations.models import Operation, OperationType


# Create your views here.


def create_operation_log(request, operation_type=None, equipment=None, cartridge=None, cartridge_old=None,
                         location_old=None, location_new=None,
                         responsible_old=None, responsible_new=None):
    Operation(operation_type=operation_type,
              date=datetime.datetime.now(),
              user=request.user,
              equipment=equipment,
              cartridge=cartridge,
              cartridge_old=cartridge_old,
              location_old=location_old if location_old else None,
              location_new=location_new,
              responsible_old=responsible_old,
              responsible_new=responsible_new).save()
