package vanet_gpsr;

import inet.node.gpsr.GpsrRouter;

//
// Mobile vehicular node for VANET implementing the GPSR (Greedy Perimeter Stateless Routing)
// protocol over an IEEE 802.11p (DSRC/WAVE) wireless network interface.
// Vehicular position and mobility are dynamically synchronized with SUMO via TraCI.
//
module VeinsGpsrCar extends GpsrRouter
{
    parameters:
        @display("i=veins/node/car;is=vs");
}
