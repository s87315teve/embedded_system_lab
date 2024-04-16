//
//  ViewController.swift
//  Bookkeeping
//
//  Created by 邱佳詮 on 2024/3/12.
//

import UIKit

class ViewController: UIViewController, UITableViewDataSource, UITableViewDelegate
{
    var dataArray = [[String:Any]]()

    @IBOutlet weak var nameField: UITextField!
    @IBOutlet weak var priceLabel: UILabel!
    @IBOutlet weak var newCostField: UITextField!
    @IBOutlet var totalCostLabel: UIView!
    @IBOutlet weak var tableView: UITableView!
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view.
        //讀檔
        loadDataArray()
        updateTotal()
    }
    @IBAction func addData(_ sender: Any) {
        //檢查輸入匡有沒有⽂字，如果沒有，離開function
        guard let newCostString = newCostField.text, !newCostString.isEmpty else { return }
        //檢查輸入的⽂字可不可以轉成 Double，如果不能，離開function
        guard let newCost = Double(newCostString) else { return }
        //檢查、取得輸入的名字
        guard let newName = nameField.text, !newName.isEmpty else
        { return }
        //取得輸入資料當下的時間
        let newDate = Date()
        //創造新的Dictionary加入array
        dataArray.append(["name":newName,"cost":newCost,"date":newDate])
        //叫table view 重新讀取⼀次資料
        tableView.reloadData()
        //存擋
        saveDataArray()
        //準備下次輸入，將輸入匡清空
        nameField.text=""
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
            
        //取得dictionary取得要顯⽰的資料的key的值
        //取得key為name的資料條件轉型成String
        //如果沒有這個key value pair 或轉型不成功，使⽤"No name"字串取代
        let name = dataArray[indexPath.row]["name"] as? String ?? "No name"
        //取得key為cost的資料條件轉型成Double
        //如果沒有這個key value pair 或轉型不成功，使⽤0.0取代
        let cost = dataArray[indexPath.row]["cost"] as? Double ?? 0.0
        //設定cell的內容
        //把name設定到cell的title
        cell.textLabel?.text = name
        //把cost設定到cell的detail title
        cell.detailTextLabel?.text = "\(cost)"
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
        saveDataArray()
        updateTotal()
    }
    func updateTotal(){
        var total:Double = 0
//        TODO:計算總額存到 total 變數
        for item in dataArray{
            let currentPrice=item["cost"] as! Double
            total+=currentPrice
        }
//        TODO:更新總額到 totalCostLabel
        priceLabel.text=String(total)
        
        // for debug
//        for item in dataArray {
//            if let name = item["name"], let cost = item["cost"], let date = item["date"] {
//                print("Name: \(name), Cost: \(cost), Date: \(date)")
//            }
//        }
        
    }
    func writeStringToFile(writeString:String, fileName:String) {
        //取得app專⽤資料夾路徑，並且確定檔案路徑存在
        guard let dir = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first else{ return}
        //在路徑後加上檔名，組合成要寫入的檔案路徑
        let fileURL = dir.appendingPathComponent(fileName)
        do{
            print("save:\n\(writeString)")
            //嘗試使⽤utf8格式寫入檔案
            try writeString.write(to: fileURL, atomically: false,
            encoding: .utf8)
        }catch
        {
            //若寫入錯誤print錯誤
            print("write error")
        }
    }
    
    func readFileToString(fileName:String) -> String {
        //取得app專⽤資料夾路徑，並且確定檔案路徑存在，如果不存在，return空字串
        guard let dir = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first else{
        return ""
        }
        //在路徑後加上檔名，組合成要讀取的檔案路徑
        let fileURL = dir.appendingPathComponent(fileName)
        //宣告要儲存讀取出來的string的變數
        var readString = ""
        do{
            //嘗試使⽤utf8格式讀取字串
            try readString = String.init(contentsOf: fileURL, encoding: .utf8)
        }catch
        {
            //若讀取錯誤print錯誤
            print("read error")
        }
        //return讀取出的string
        return readString
    }
    
    func saveDataArray(){
        //宣告儲存最後string的變數
        var finalString = ""
        //iterate array 裡所有的 element
        for dictionary in dataArray {
            //your code: 將dictionary轉成csv⼀筆資料的格式，更新finalString
            let formatter = DateFormatter()
            formatter.dateFormat = "yyyy-MM-dd HH:mm"
            let currentDate=formatter.string(from: dictionary["date"] as! Date)
            let currentName=dictionary["name"] as! String
            let currentCost = String(dictionary["cost"] as! Double)
            let values = [currentDate, currentName, currentCost]
            finalString += values.joined(separator: ",") + "\n"
            
        }
        //寫入data.txt檔案
        writeStringToFile(writeString: finalString, fileName: "data.txt")
    }
    
    func loadDataArray() {
        //宣告儲存Array最後的結果的變數
        var finalArray = [[String:Any]]()
        //讀取data.txt的檔案內容
        let csvString = readFileToString(fileName: "data.txt")
        print("load data:\n\(csvString)")
        //⽤"\n"將每⼀筆資料分開
        let lineOfString = csvString.components(separatedBy: "\n")
        //iterate 每⼀筆資料的string
        for line in lineOfString {
            print("line: \(line)")
            if line.isEmpty{
                break
            }

            let stringArray=line.components(separatedBy: ",")
            print(stringArray)
            
            
            //將這筆資料的string轉成dictionary的格式
            //your code here
            //將讀取出的這筆資料加入array
            //your code here
            let formatter = DateFormatter()
            formatter.dateFormat = "yyyy-MM-dd HH:mm"
            let currentDate=formatter.date(from: stringArray[0])
            let currentName=stringArray[1]
            let currentCost=stringArray[2]
            
            finalArray.append(["name":currentName,"cost":Double(currentCost)!,"date":currentDate])
        }
        //將讀取出的finalArray取代掉原本的dataArray
        dataArray = finalArray
        print("dataArray:\n\(dataArray)")
        //更新 tableview 與 介⾯資料
        tableView.reloadData()
        updateTotal()
    }
    
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {

     //利⽤segue找到它連到的viewcontroller
     //並且確定type是DetailViewController
     guard let detailVC = (segue.destination as? DetailViewController) else { return }

     //取得使⽤者點選的位置
     guard let selectedIndex = tableView.indexPathForSelectedRow?.row else { return }

     //取得點選到的data
     let selectedData = dataArray[selectedIndex]

     //將data設定到第⼆個⾴⾯的property上
     detailVC.data = selectedData

     }
    
    @IBAction func unwindFromDetailVC(segue:UIStoryboardSegue)
     {
    
     //利⽤segue找到它來源的viewcontroller
     //並且確定type是DetailViewControlle
     guard let detailVC = segue.source as? DetailViewController else
    { return }

     //取得使⽤者點選的位置，當作欲修改data array的位置
     guard let selectedIndex = tableView.indexPathForSelectedRow?.row else {return}
         print("selectedIndex: \(selectedIndex)")
     //更新array中的dictionary
     dataArray[selectedIndex] = detailVC.data
         print(dataArray)
         print("HIIIIII")
         print("\(detailVC.data)")
     //更新對應的tableview的row
     tableView.reloadRows(at: [tableView.indexPathForSelectedRow!], with: .automatic)
     updateTotal()
     saveDataArray()
     }

}

