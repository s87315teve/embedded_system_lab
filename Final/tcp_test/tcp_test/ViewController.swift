//
//  ViewController.swift
//  tcp_test
//
//  Created by 邱佳詮 on 2024/5/14.
//

import UIKit

class ViewController: UIViewController, StreamDelegate {

    @IBOutlet weak var connectButton: UIButton!
    @IBOutlet weak var hostIPTextfield: UITextField!
    @IBOutlet weak var resetButton: UIButton!
    @IBOutlet weak var serverMsgLabel: UILabel!
    @IBOutlet weak var statusLabel: UILabel!
    @IBOutlet weak var sendButton: UIButton!
    @IBOutlet weak var inputTextField: UITextField!
    private var inputStream: InputStream?
    private var outputStream: OutputStream?
    
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view.
//        let hostIP=hostIPTextfield.text!
//        setupNetworkCommunication(hostIP: hostIP)
    }
    
    @IBAction func connectButtonPressed(_ sender: Any) {
        let hostIP=hostIPTextfield.text!
        setupNetworkCommunication(hostIP: hostIP)
        statusLabel.text="connect to server: \(hostIP)"
        
    }
    @IBAction func resetButtonPressed(_ sender: Any) {
        let hostIP=hostIPTextfield.text!
        setupNetworkCommunication(hostIP: hostIP)
        statusLabel.text="reset finished"
    }
    func setupNetworkCommunication(hostIP: String) {
            var readStream: Unmanaged<CFReadStream>?
            var writeStream: Unmanaged<CFWriteStream>?
            
            // 替換"your.server.ip"和1234為你的服務器IP地址和端口
            CFStreamCreatePairWithSocketToHost(nil, hostIP as CFString, 6000, &readStream, &writeStream)
            
            inputStream = readStream?.takeRetainedValue()
            outputStream = writeStream?.takeRetainedValue()
            
            inputStream?.delegate = self
            outputStream?.delegate = self
            
            inputStream?.schedule(in: .current, forMode: .common)
            outputStream?.schedule(in: .current, forMode: .common)
            
            inputStream?.open()
            outputStream?.open()
        statusLabel.text="finish initializaiton"
    }
    
    @IBAction func sendButtonTapped(_ sender: UIButton) {
        let data = inputTextField.text ?? ""
                sendData(data)
        inputTextField.text=""
        statusLabel.text="send msg"
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

