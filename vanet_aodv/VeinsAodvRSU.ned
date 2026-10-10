package vanet_aodv;

import inet.node.aodv.AodvRouter;

//
// Road-Side Unit (RSU) / Node infrastruktur statis untuk skenario V2I (Vehicle-to-Infrastructure).
// Bertindak sebagai server pengumpul data trafik / gateway darurat dengan protokol routing AODV.
//
module VeinsAodvRSU extends AodvRouter
{
    parameters:
        @display("i=device/antennatower;is=m");
}
