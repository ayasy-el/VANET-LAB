package vanet_aodv;

import inet.node.aodv.AodvRouter;

//
// Modul kendaraan bergerak untuk VANET yang mengimplementasikan protokol routing AODV
// di atas antarmuka nirkabel IEEE 802.11p (DSRC/WAVE).
// Posisi dan mobilitas kendaraan disinkronisasikan secara dinamis dengan SUMO via TraCI.
//
module VeinsAodvCar extends AodvRouter
{
    parameters:
        @display("i=veins/node/car;is=vs");
}
