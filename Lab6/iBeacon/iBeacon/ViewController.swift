//
//  ViewController.swift
//  iBeacon
//
//  Created by 邱佳詮 on 2024/4/16.
//

import UIKit
import CoreLocation

class ViewController: UIViewController, CLLocationManagerDelegate  {
    var locationManager: CLLocationManager = CLLocationManager()
    @IBOutlet weak var rangingResultTextView: UITextView!
    @IBOutlet weak var monitorResultTextView: UITextView!
    let uuid = "A3E1C063-9235-4B25-AA84-D249950AADC4"
    let identfier = "esd region"
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view.
        if CLLocationManager.isMonitoringAvailable(for: CLBeaconRegion.self){
            if CLLocationManager.authorizationStatus() !=
                CLAuthorizationStatus.authorizedAlways
            {
                locationManager.requestAlwaysAuthorization()
            }
        }
        //創造包含同樣 uuid 的 beacon 的 region
        let region = CLBeaconRegion(uuid: UUID.init(uuidString: uuid)!,
                                    identifier: identfier)
        
        //設定 locaiton manager 的 delegate
        locationManager.delegate = self
        //設定region monitoring 要被通知的時機
        region.notifyEntryStateOnDisplay = true
        region.notifyOnEntry = true
        region.notifyOnExit = true
        //開始 monitoring
        locationManager.startMonitoring(for: region)
    }
    func locationManager(_ manager: CLLocationManager, didStartMonitoringFor region: CLRegion) {
        //將成功開始 monitor 的 region 的 identifier 加入到 monitor textview 最上方
        monitorResultTextView.text = "did start monitoring \(region.identifier)\n" +
        monitorResultTextView.text
    }
    func locationManager(_ manager: CLLocationManager, didEnterRegion region: CLRegion) {
        //將偵測到進入 region 的狀態加入到 monitor textview 最上方
        monitorResultTextView.text = "did enter\n" + monitorResultTextView.text
    }
    func locationManager(_ manager: CLLocationManager, didExitRegion region: CLRegion) {
        //將偵測到離開 region 的狀態加入到 monitor textview 最上方
        monitorResultTextView.text = "did exit\n" + monitorResultTextView.text
    }
    func locationManager(_ manager: CLLocationManager, didDetermineState state: CLRegionState, for region: CLRegion) {
        switch state {
            case .inside:
                //將偵測到在 region 內的狀態加入到 monitor textview 最上方
                monitorResultTextView.text = "state inside\n" + monitorResultTextView.text
                //如果 device 支援 ranging iBeacon，開始 ranging 這個 region
                manager.startRangingBeacons(satisfying: CLBeaconIdentityConstraint(uuid: UUID.init(uuidString: uuid)!))
            case .outside:
                //將偵測到在 region 外的狀態加入到 monitor textview 最上方
                monitorResultTextView.text = "state outside\n" + monitorResultTextView.text
                //停止 ranging region
                manager.stopMonitoring(for: region)
            default:
                break
        }
    }
    
    func locationManager(_ manager: CLLocationManager, didRangeBeacons beacons: [CLBeacon], in region: CLBeaconRegion) {
    //清空原本的ranging textview
    rangingResultTextView.text = ""
    //iterate 每個收到的 beacon
    for beacon in beacons {
        //根據不同 proximity 常數設定 proximityString
        var proximityString = ""
        switch beacon.proximity {
            case .far:
                proximityString = "far"
            case .near:
                proximityString = "near"
            case .immediate:
                proximityString = "immediate"
            default :
                proximityString = "unknow"
        }
        //把這個beacon的數值放到ranging textview上
        rangingResultTextView.text = rangingResultTextView.text + "Major: \(beacon.major)" + " Minor: \(beacon.minor)" + " RSSI: \(beacon.rssi)" + " Proximity: \(proximityString)" + " Accuracy: \(beacon.accuracy)" + "\n\n";
    }
    }

}

