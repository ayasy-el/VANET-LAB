package vanet_aodv;

import inet.node.aodv.AodvRouter;

//
// Mobile vehicular node for VANET implementing the AODV routing protocol
// over an IEEE 802.11p (DSRC/WAVE) wireless network interface.
// Vehicular position and mobility are dynamically synchronized with SUMO via TraCI.
//
module VeinsAodvCar extends AodvRouter
{
    parameters:
        @display("i=veins/node/car;is=vs");
}
