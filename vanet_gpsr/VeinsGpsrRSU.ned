package vanet_gpsr;

import inet.node.gpsr.GpsrRouter;

//
// Static Road-Side Unit (RSU) infrastructure node for V2I (Vehicle-to-Infrastructure) scenarios.
// Operates as a central traffic telemetry collector / emergency gateway with GPSR routing support.
//
module VeinsGpsrRSU extends GpsrRouter
{
    parameters:
        @display("i=device/antennatower;is=m");
}
