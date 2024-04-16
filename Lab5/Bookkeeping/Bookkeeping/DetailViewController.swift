//
//  DetailViewController.swift
//  Bookkeeping
//
//  Created by 邱佳詮 on 2024/4/2.
//

import UIKit

class DetailViewController: UIViewController {

    @IBOutlet weak var nameField: UITextField!
    @IBOutlet weak var costField: UITextField!
    @IBOutlet weak var dateLabel: UILabel!
    var data: [String:Any]!
    override func viewDidLoad() {
        super.viewDidLoad()
//        print(data)
        let name=data["name"] as? String
        let cost=data["cost"] as! Double
        
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd HH:mm"
        let currentDate=formatter.string(from: data["date"] as! Date)
        dateLabel.text=currentDate
        nameField.text=name
        costField.text="\(cost)"


        // Do any additional setup after loading the view.
    }
    
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
     // your code here
     //將 nameField的字串抓出來轉換成String
     //將 costField的字串抓出來轉換成Double
        guard let newName = nameField.text, !newName.isEmpty else
        { return }
        
        guard let newCostString = costField.text, !newCostString.isEmpty else { return }
        guard let newCost = Double(newCostString) else { return }
     //更新 data property，讓第⼀⾴ViewController抓到新的data資料
        print("newCost:\(newCost)")
        print("newName:\(newName)")
     data["name"] = newName
     data["cost"] = newCost

     }

    /*
    // MARK: - Navigation

    // In a storyboard-based application, you will often want to do a little preparation before navigation
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // Get the new view controller using segue.destination.
        // Pass the selected object to the new view controller.
    }
    */

}
