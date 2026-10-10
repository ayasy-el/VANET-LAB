package vanet_aodv;

import inet.node.aodv.AodvRouter;

//
// Static Road-Side Unit (RSU) infrastructure node for V2I (Vehicle-to-Infrastructure) scenarios.
// Operates as a central traffic telemetry collector / emergency gateway with AODV routing support.
//
module VeinsAodvRSU extends AodvRouter
{
    parameters:
        @display("i=device/antennatower;is=m");
}
