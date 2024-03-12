//
//  ViewController.swift
//  Bookkeeping
//
//  Created by 邱佳詮 on 2024/3/12.
//

import UIKit

class ViewController: UIViewController, UITableViewDataSource, UITableViewDelegate
{
    var dataArray:[Double] = [123, 456, 789]

    @IBOutlet weak var priceLabel: UILabel!
    @IBOutlet weak var newCostField: UITextField!
    @IBOutlet var totalCostLabel: UIView!
    @IBOutlet weak var tableView: UITableView!
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view.
        updateTotal()
    }
    @IBAction func addData(_ sender: Any) {
        //檢查輸入匡有沒有⽂字，如果沒有，離開function
        guard let newCostString = newCostField.text, !newCostString.isEmpty else { return }
        //檢查輸入的⽂字可不可以轉成 Double，如果不能，離開function
        guard let newCost = Double(newCostString) else { return }
        
        
        //將新的數值加入array
        dataArray.append(newCost)
        //叫table view 重新讀取⼀次資料
        tableView.reloadData()
        //準備下次輸入，將輸入匡清空
        newCostField.text = ""
        //將鍵盤收起
        newCostField.resignFirstResponder()
        //創立指向新增資料所在的table位置的IndexPath物件
        updateTotal()
    }
    
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
    return dataArray.count
    }
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
    //從storyboard中的table view尋找有 identifier 為"Basic Cell"的 cell 範例
    //且如果之前有相同identifier的Cell被宣告出來且沒有在⽤的話，重複使⽤，節省記憶體
    let cell = tableView.dequeueReusableCell(withIdentifier: "Basic Cell", for: indexPath)
        
    //設定cell的內容
    cell.textLabel?.text = "\(dataArray[indexPath.row])"
    return cell
    }
    
    func tableView(_ tableView: UITableView, canEditRowAt indexPath: IndexPath) -> Bool {
    //我們讓 edit 的功能在每個位置的row都啟⽤。
    return true
    }
    
    func tableView(_ tableView: UITableView, commit editingStyle: UITableViewCell.EditingStyle, forRowAt indexPath: IndexPath) {
        switch editingStyle {
        case .delete: //如果是 commit delete 的動作
        dataArray.remove(at: indexPath.row ) //從 array 移除資料
        //告訴table view要刪掉這些位置(array)的資料，的row，使⽤往上刪除的動畫
        tableView.deleteRows(at: [indexPath], with: .top)
        default: //其他edit的動作不做任何事
        break
        }
        updateTotal()
    }
    func updateTotal(){
        var total:Double = 0
//        TODO:計算總額存到 total 變數
        for currentPrice in dataArray{
            total+=Double(currentPrice)
        }
//        TODO:更新總額到 totalCostLabel
        priceLabel.text=String(total)
        
    }

}

