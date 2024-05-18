//
//  ViewController.swift
//  iBeacon
//
//  Created by 邱佳詮 on 2024/4/16.
//

import UIKit
import CoreLocation

class ViewController: UIViewController, CLLocationManagerDelegate, StreamDelegate {

    @IBOutlet weak var portTextField: UITextField!
    @IBOutlet weak var serverMsgLabel: UILabel!
    @IBOutlet weak var resetButton: UIButton!
    @IBOutlet weak var hostIPTextfield: UILabel!
    @IBOutlet weak var connectButton: UIButton!
    var locationManager: CLLocationManager = CLLocationManager()
    @IBOutlet weak var rangingResultTextView: UITextView!
    @IBOutlet weak var monitorResultTextView: UITextView!
    var beaconsData: [[String: Any]] = []
    private var inputStream: InputStream?
    private var outputStream: OutputStream?
    var connectionLabel=true
    let uuid = "A3E1C063-9235-4B25-AA84-D249950AADC4"
    let identfier = "esd region"
    override func viewDidLoad() {
        super.viewDidLoad()
        setupNetworkCommunication(hostIP: "0", port: 0)
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
    beaconsData=[]
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
        let beaconData: [String: Any] = [
                "Major": beacon.major,
                "Minor": beacon.minor,
                "RSSI": beacon.rssi,
                "Proximity": proximityString,
                "Accuracy": beacon.accuracy
            ]
            
            beaconsData.append(beaconData)
        // 將 beaconsData 轉換為 JSON
        if connectionLabel{
            do {
                let jsonData = try JSONSerialization.data(withJSONObject: beaconsData, options: .prettyPrinted)
                let jsonString = String(data: jsonData, encoding: .utf8) ?? ""
                //            rangingResultTextView.text = jsonString
//                print("ready to send")
                sendData(jsonString)
                print("sended")
            } catch {
                print("Error creating JSON: \(error)")
            }
        }
        
        
        
        }
    }


    @IBAction func resetButtonPressed(_ sender: Any) {
        print("pressed reset button")
        let hostIP=hostIPTextfield.text!
        let port=Int(portTextField.text!)!
        setupNetworkCommunication(hostIP: hostIP, port: port)
        print("finish connection")
        connectionLabel=true
    }
    @IBAction func connectButtonPressed(_ sender: Any) {
        print("pressed connect button")
        let hostIP=hostIPTextfield.text!
        let port=Int(portTextField.text!)!
        setupNetworkCommunication(hostIP: hostIP, port: port)
        print("finish connection")
    //        statusLabel.text="connect to server: \(hostIP)"
        connectionLabel=true
        
    }
    
    func setupNetworkCommunication(hostIP: String, port: Int) {
            var readStream: Unmanaged<CFReadStream>?
            var writeStream: Unmanaged<CFWriteStream>?
            
            // 替換"your.server.ip"和1234為你的服務器IP地址和端口
//        CFStreamCreatePairWithSocketToHost(nil, hostIP as CFString, 6000, &readStream, &writeStream)
        CFStreamCreatePairWithSocketToHost(nil, "172.20.10.2" as CFString, 6000, &readStream, &writeStream)
            
            inputStream = readStream?.takeRetainedValue()
            outputStream = writeStream?.takeRetainedValue()
            
            inputStream?.delegate = self
            outputStream?.delegate = self
            
            inputStream?.schedule(in: .current, forMode: .common)
            outputStream?.schedule(in: .current, forMode: .common)
            
            inputStream?.open()
            outputStream?.open()
//        statusLabel.text="finish initializaiton"
    }
    func sendData(_ data: String) {
            let data = data.data(using: .utf8)!
            _ = data.withUnsafeBytes {
                outputStream?.write($0.bindMemory(to: UInt8.self).baseAddress!, maxLength: data.count)
            }
    }
    
    func stream(_ aStream: Stream, handle eventCode: Stream.Event) {
            switch eventCode {
            case .hasBytesAvailable:
                readAvailableBytes(stream: aStream as! InputStream)
            case .errorOccurred:
                print("Error with stream: \(String(describing: aStream.streamError))")
            case .endEncountered:
                closeStreams()
            default:
                break
            }
    }
    
    private func readAvailableBytes(stream: InputStream) {
            let buffer = UnsafeMutablePointer<UInt8>.allocate(capacity: 1024)
            while stream.hasBytesAvailable {
                let numberOfBytesRead = inputStream?.read(buffer, maxLength: 1024) ?? 0
                
                if numberOfBytesRead < 0, let error = stream.streamError {
                    print(error)
                    break
                }
                
                // 使用緩存數據構建字符串
                if let output = String(bytesNoCopy: buffer, length: numberOfBytesRead, encoding: .utf8, freeWhenDone: true) {
                    DispatchQueue.main.async {
                        self.serverMsgLabel.text = output
                    }
                }
            }
    }
    
    private func closeStreams() {
            inputStream?.close()
            outputStream?.close()
            inputStream?.remove(from: .current, forMode: .common)
            outputStream?.remove(from: .current, forMode: .common)
            inputStream = nil
            outputStream = nil
        }
}

