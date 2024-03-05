//
//  ViewController.swift
//  Hello
//
//  Created by 邱佳詮 on 2024/2/27.
//

import UIKit

class ViewController: UIViewController {

    @IBOutlet weak var nameTextField: UITextField!
    @IBOutlet weak var helloLabel: UILabel!
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view.
    }
    @IBAction func sayHelloPressed(_ sender: Any) {
        //將在nameTextField的內容合成新的字串
        let helloString = "Hello \(nameTextField.text!)!"
        //設定helloString字串到
        helloLabel.text = helloString
        //清空nameTextField輸入匡
        nameTextField.text = ""
    }
    

}

