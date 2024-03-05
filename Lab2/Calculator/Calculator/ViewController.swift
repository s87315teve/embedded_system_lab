//
//  ViewController.swift
//  Calculator
//
//  Created by 邱佳詮 on 2024/3/5.
//

import UIKit

class ViewController: UIViewController {


    @IBOutlet weak var digitLabel: UITextField!
    @IBOutlet weak var operatorLabel: UITextField!
    //表⽰下⼀次按digit按鈕時要開始輸入⼀個新的數字
    var shouldStartNewNumberInput = false
    //按下operator前輸入的數字暫存在這裡
    var pendendingNumber = ""
    var continueCalculateFlag=false
    var globalValue1=Double()
    var globalValue2=Double()
    var globalOperatorString=String()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view.
        //初始化數字及運算⼦的狀態
        digitLabel.text = "0"
        self.operatorLabel.text=""
        shouldStartNewNumberInput = false
        pendendingNumber = ""
        continueCalculateFlag=false
    }

    @IBAction func button_0(_ sender: UIButton) {
        //判斷是否開始新的數字輸入
        if shouldStartNewNumberInput{
        //暫存前⼀個輸入的數字
        pendendingNumber = digitLabel.text!
        //初始化數字輸入匡，初始值是0，與viewDidLoad⼀樣
        //(剛按下的新的digit在if過後會放到digitLabel)
        digitLabel.text = "0"
        //開始新的數字輸入了，把flag改回來
        shouldStartNewNumberInput = false
        }
        //如果按下按鈕時，digitLabel為初始0的狀態，把初始的0刪掉後再開始輸入
        if digitLabel.text == "0"{
        digitLabel.text = ""
        }
        //將 sender button 的⽂字接在 digirLabel的⽂字後⽅
        digitLabel.text = digitLabel.text! + sender.titleLabel!.text!
    }
    @IBAction func button_1(_ sender: UIButton) {
        if shouldStartNewNumberInput{
            pendendingNumber = digitLabel.text!
            digitLabel.text = "0"
            shouldStartNewNumberInput = false
        }
        
        if digitLabel.text == "0"{
        digitLabel.text = ""
        }
        digitLabel.text = digitLabel.text! + sender.titleLabel!.text!
    }
    @IBAction func button_2(_ sender: UIButton) {
        if shouldStartNewNumberInput{
            pendendingNumber = digitLabel.text!
            digitLabel.text = "0"
            shouldStartNewNumberInput = false
        }
        
        if digitLabel.text == "0"{
        digitLabel.text = ""
        }
        digitLabel.text = digitLabel.text! + sender.titleLabel!.text!
    }
    
    @IBAction func button_3(_ sender: UIButton) {
        if shouldStartNewNumberInput{
            pendendingNumber = digitLabel.text!
            digitLabel.text = "0"
            shouldStartNewNumberInput = false
        }
        
        if digitLabel.text == "0"{
        digitLabel.text = ""
        }
        digitLabel.text = digitLabel.text! + sender.titleLabel!.text!
    }
    @IBAction func button_4(_ sender: UIButton) {
        if shouldStartNewNumberInput{
            pendendingNumber = digitLabel.text!
            digitLabel.text = "0"
            shouldStartNewNumberInput = false
        }
        
        if digitLabel.text == "0"{
        digitLabel.text = ""
        }
        digitLabel.text = digitLabel.text! + sender.titleLabel!.text!
    }
    @IBAction func button_5(_ sender: UIButton) {
        if shouldStartNewNumberInput{
            pendendingNumber = digitLabel.text!
            digitLabel.text = "0"
            shouldStartNewNumberInput = false
        }
        
        if digitLabel.text == "0"{
        digitLabel.text = ""
        }
        digitLabel.text = digitLabel.text! + sender.titleLabel!.text!
    }
    @IBAction func button_6(_ sender: UIButton) {
        if shouldStartNewNumberInput{
            pendendingNumber = digitLabel.text!
            digitLabel.text = "0"
            shouldStartNewNumberInput = false
        }
        
        if digitLabel.text == "0"{
        digitLabel.text = ""
        }
        digitLabel.text = digitLabel.text! + sender.titleLabel!.text!
    }
    @IBAction func button_7(_ sender: UIButton) {
        if shouldStartNewNumberInput{
            pendendingNumber = digitLabel.text!
            digitLabel.text = "0"
            shouldStartNewNumberInput = false
        }
        
        if digitLabel.text == "0"{
        digitLabel.text = ""
        }
        digitLabel.text = digitLabel.text! + sender.titleLabel!.text!
    }
    @IBAction func button_8(_ sender: UIButton) {
        if shouldStartNewNumberInput{
            pendendingNumber = digitLabel.text!
            digitLabel.text = "0"
            shouldStartNewNumberInput = false
        }
        
        if digitLabel.text == "0"{
        digitLabel.text = ""
        }
        digitLabel.text = digitLabel.text! + sender.titleLabel!.text!
    }
    @IBAction func button_9(_ sender: UIButton) {
        if shouldStartNewNumberInput{
            pendendingNumber = digitLabel.text!
            digitLabel.text = "0"
            shouldStartNewNumberInput = false
        }
        
        if digitLabel.text == "0"{
        digitLabel.text = ""
        }
        digitLabel.text = digitLabel.text! + sender.titleLabel!.text!
    }
    @IBAction func button_point(_ sender: UIButton) {
        //為了不讓⼀個數字出現兩個"."，如果按下"."且原本的數字已經有"."，則跳出
        if digitLabel.text?.range(of: ".") != nil
        {
            return
        }
        else if digitLabel.text=="-"{
            digitLabel.text="-0."
            
        }
        else{
            digitLabel.text = digitLabel.text! + sender.titleLabel!.text!
        }
    }
    
    @IBAction func button_plus(_ sender: UIButton) {
        if self.operatorLabel.text != ""
        {
            guard let operatorString = operatorLabel.text,
            !operatorString.isEmpty
            else { return}
            //檢查 pendingNumber 與 digitLabel 的字串可否轉成數字，若不⾏則離開
            //若可以轉成數字，unwrap成Double存到value1, value2
            guard let value1 = Double(pendendingNumber),
            let value2 = Double(digitLabel.text!) else { return}
            
            //暫存計算結果的變數
            var result:Double = 0
            //根據不同的 operator 做計算
            switch operatorString {
            case "+":
            result = value1 + value2
            case "-":
            result = value1 - value2
            case "x":
            result = value1 * value2
            case "÷":
            result = value1 / value2
            // ... add your own case
            default:
            break;
            }
            //將計算的結果顯⽰在 digitLabel
            digitLabel.text = "\(result)"
            //將螢幕上的運算⼦清空

             
        }
        
        
        //將 sender button 的⽂字取代 operatorLabel 原有的⽂字
        self.operatorLabel.text = sender.titleLabel?.text
        //已按下運算⼦，下⼀個digit輸入時應該開始新的數字輸入
        shouldStartNewNumberInput = true
        globalOperatorString=(sender.titleLabel?.text)!
        continueCalculateFlag=false
    }
    @IBAction func button_minus(_ sender: UIButton) {
        if self.operatorLabel.text != ""
        {
            guard let operatorString = operatorLabel.text,
            !operatorString.isEmpty
            else { return}
            //檢查 pendingNumber 與 digitLabel 的字串可否轉成數字，若不⾏則離開
            //若可以轉成數字，unwrap成Double存到value1, value2
            guard let value1 = Double(pendendingNumber),
            let value2 = Double(digitLabel.text!) else { return}
            
            //暫存計算結果的變數
            var result:Double = 0
            //根據不同的 operator 做計算
            switch operatorString {
            case "+":
            result = value1 + value2
            case "-":
            result = value1 - value2
            case "x":
            result = value1 * value2
            case "÷":
            result = value1 / value2
            // ... add your own case
            default:
            break;
            }
            //將計算的結果顯⽰在 digitLabel
            digitLabel.text = "\(result)"
            //將螢幕上的運算⼦清空

             
        }
        //如果按下按鈕時，digitLabel為0，直接在後面加上負號
        if digitLabel.text == "0"{
        digitLabel.text = "-"
        }
        else{
            self.operatorLabel.text = sender.titleLabel?.text
            //已按下運算⼦，下⼀個digit輸入時應該開始新的數字輸入
            shouldStartNewNumberInput = true
        }
        globalOperatorString=(sender.titleLabel?.text)!
        continueCalculateFlag=false
    }
    @IBAction func button_multiply(_ sender: UIButton) {
        if self.operatorLabel.text != ""
        {
            guard let operatorString = operatorLabel.text,
            !operatorString.isEmpty
            else { return}
            //檢查 pendingNumber 與 digitLabel 的字串可否轉成數字，若不⾏則離開
            //若可以轉成數字，unwrap成Double存到value1, value2
            guard let value1 = Double(pendendingNumber),
            let value2 = Double(digitLabel.text!) else { return}
            
            //暫存計算結果的變數
            var result:Double = 0
            //根據不同的 operator 做計算
            switch operatorString {
            case "+":
            result = value1 + value2
            case "-":
            result = value1 - value2
            case "x":
            result = value1 * value2
            case "÷":
            result = value1 / value2
            // ... add your own case
            default:
            break;
            }
            //將計算的結果顯⽰在 digitLabel
            digitLabel.text = "\(result)"
            //將螢幕上的運算⼦清空

             
        }
        self.operatorLabel.text = sender.titleLabel?.text
        //已按下運算⼦，下⼀個digit輸入時應該開始新的數字輸入
        shouldStartNewNumberInput = true
        globalOperatorString=(sender.titleLabel?.text)!
        continueCalculateFlag=false
    }
    @IBAction func button_divide(_ sender: UIButton) {
        if self.operatorLabel.text != ""
        {
            guard let operatorString = operatorLabel.text,
            !operatorString.isEmpty
            else { return}
            //檢查 pendingNumber 與 digitLabel 的字串可否轉成數字，若不⾏則離開
            //若可以轉成數字，unwrap成Double存到value1, value2
            guard let value1 = Double(pendendingNumber),
            let value2 = Double(digitLabel.text!) else { return}
            
            //暫存計算結果的變數
            var result:Double = 0
            //根據不同的 operator 做計算
            switch operatorString {
            case "+":
            result = value1 + value2
            case "-":
            result = value1 - value2
            case "x":
            result = value1 * value2
            case "÷":
            result = value1 / value2
            // ... add your own case
            default:
            break;
            }
            //將計算的結果顯⽰在 digitLabel
            digitLabel.text = "\(result)"
            //將螢幕上的運算⼦清空

             
        }
        self.operatorLabel.text = sender.titleLabel?.text
        //已按下運算⼦，下⼀個digit輸入時應該開始新的數字輸入
        shouldStartNewNumberInput = true
        globalOperatorString=(sender.titleLabel?.text)!
        continueCalculateFlag=false
    }
    
    @IBAction func button_equal(_ sender: UIButton) {
        //檢查operatorLabel有沒有值，如果是nil或是空字串，則離開function
        
        if continueCalculateFlag{
            //暫存計算結果的變數
            var result:Double = 0
            //根據不同的 operator 做計算
            switch globalOperatorString {
            case "+":
            result = globalValue1 + globalValue2
            case "-":
            result = globalValue1 - globalValue2
            case "x":
            result = globalValue1 * globalValue2
            case "÷":
            result = globalValue1 / globalValue2
            // ... add your own case
            default:
            break;
            }
            //將計算的結果顯⽰在 digitLabel
            digitLabel.text = "\(result)"
            //將螢幕上的運算⼦清空
//            operatorLabel.text = ""
            //按下等號後，下⼀次按Digit為輸入⼀個新的數字(第⼀個運算數字)
            globalValue1=result
            
        }
        else{
            guard let operatorString = operatorLabel.text,
            !operatorString.isEmpty
            else { return}
            //檢查 pendingNumber 與 digitLabel 的字串可否轉成數字，若不⾏則離開
            //若可以轉成數字，unwrap成Double存到value1, value2
            guard let value1 = Double(pendendingNumber),
                  let value2 = Double(digitLabel.text!) else { return}
            
            //暫存計算結果的變數
            var result:Double = 0
            //根據不同的 operator 做計算
            switch operatorString {
            case "+":
                result = value1 + value2
            case "-":
                result = value1 - value2
            case "x":
                result = value1 * value2
            case "÷":
                result = value1 / value2
                // ... add your own case
            default:
                break;
            }
            //將計算的結果顯⽰在 digitLabel
            digitLabel.text = "\(result)"
            //將螢幕上的運算⼦清空
            operatorLabel.text = ""
            //按下等號後，下⼀次按Digit為輸入⼀個新的數字(第⼀個運算數字)
            shouldStartNewNumberInput = true
            
            globalValue1=result
            globalValue2=value2
            globalOperatorString=operatorString
            continueCalculateFlag=true
        }
        
    }
    @IBAction func button_AC(_ sender: UIButton) {
        digitLabel.text = "0"
        self.operatorLabel.text=""
        shouldStartNewNumberInput = false
        pendendingNumber = ""
        continueCalculateFlag=false
        
    }
    @IBAction func button_back(_ sender: UIButton) {
        digitLabel.text=String(digitLabel.text!.dropLast())
        if digitLabel.text == "" {
        digitLabel.text = "0"
        }

        
    }
}

