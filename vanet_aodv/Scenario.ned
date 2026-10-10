package vanet_aodv;

import inet.physicallayer.wireless.ieee80211.packetlevel.Ieee80211DimensionalRadioMedium;
import org.car2x.veins.subprojects.veins_inet.VeinsInetManager;
import inet.visualizer.common.IntegratedVisualizer;
import inet.environment.common.PhysicalEnvironment;
import org.car2x.veins.visualizer.roads.RoadsCanvasVisualizer;

//
// Topologi Jaringan Skenario VANET dengan Routing Protokol AODV
//
network Scenario
{
    parameters:
        int numRsu = default(0);
        @display("bgb=2500,2000");
    submodules:
        radioMedium: Ieee80211DimensionalRadioMedium {
            @display("p=150,100");
        }
        manager: VeinsInetManager {
            @display("p=150,200");
        }
        visualizer: IntegratedVisualizer {
            @display("p=150,300");
        }
        physicalEnvironment: PhysicalEnvironment {
            @display("p=150,400");
        }
        roadsCanvasVisualizer: RoadsCanvasVisualizer {
            @display("p=150,500");
        }
        rsu[numRsu]: VeinsAodvRSU {
            @display("p=1040,868");
        }
        node[0]: VeinsAodvCar;
}
