export PYBINDPLUGIN=`/usr/bin/env python3 -c 'import pyangbind; import os; print ("{}/plugin".format(os.path.dirname(pyangbind.__file__)))'`

pyang --plugindir $PYBINDPLUGIN -f pybind -o sno.py ../yang/* ../device/yang/device.yang ../device/yang/CumulusLinux/*

pyang --plugindir $PYBINDPLUGIN -f pybind -o odl.py ../device/yang/odl/*