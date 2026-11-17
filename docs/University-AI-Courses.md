# 大學 AI 課程資源：史丹佛、MIT、清華、北大、浙大

> 資料日期：2026-11-17  
> 範圍：整理史丹佛、MIT、清華、北大、浙大公開的 AI 相關課程入口，每一門都附連結；偏重機器學習、深度學習、NLP 與 LLM，並列出補數學基礎的課。  
> 讀法：每個連結都標示驗證狀態——**✅** 表示連結是搜尋結果直接回傳的官方或平台網址；**🔎** 表示網址取自第三方文章或是該校慣用的位置，沒有在搜尋結果裡直接看到，請自行核對。**我沒有開啟任何課程頁面**（沙箱連不到這些網站），所以開課學期、是否仍開放、是否有錄影，都以各頁面現況為準。  
> 與本庫其他資源的關係：非校園系列的課程（Karpathy、李宏毅、吳恩達等）見 [AI 學習資源](AI-Learning-Resources.md)。

## 先看結論

- **英文、系統化**：史丹佛的 CS229（機器學習）、CS231n（視覺）、CS224N（NLP）、CS336（從零寫語言模型），以及 MIT 的 6.S191（深度學習入門）。
- **補數學**：MIT OpenCourseWare 的 18.06SC（線性代數）與 18.065（機器學習的矩陣方法）。
- **中文、有平台**：浙大《機器學習》《人工智能：模型與算法》在中國大學 MOOC；清華在學堂在線有三門 AI 相關課程；北大有《人工智能原理》。
- **這次沒查到的**：北大、清華、浙大專門講「大模型」的公開課；北大的深度學習課程。這不代表它們沒有，只是我在可用的搜尋範圍內沒找到可確認的連結。
- 這份清單是入口，不評價課程品質，我也沒有逐一上完。

---

## 1. 學校 × 主題：這次查到什麼

![圖：史丹佛、MIT、清華、北大、浙大在機器學習、NLP 與 LLM、數學基礎、AI 概論四個主題查到的課程](figures/university-ai-courses-matrix.svg)

---

## 2. 史丹佛大學（Stanford）

| 課程 | 內容 | 連結 | 狀態 |
|---|---|---|---|
| CS224N：*Natural Language Processing with Deep Learning* | NLP 與深度學習。目前這一期的投影片在 `slides_w26` 之下；課程網站列出的歷年錄影存檔包含 Spring 2024、Winter 2023、Winter 2021、Winter 2019、Winter 2017。官方 YouTube 播放清單我沒有確認 | [課程網站](https://web.stanford.edu/class/cs224n/)、[2026 第 1 講投影片](https://web.stanford.edu/class/cs224n/slides_w26/cs224n-2026-lecture01-intro.pdf) | ✅ |
| CS336：*Language Modeling from Scratch* | Percy Liang 與 Tatsunori Hashimoto 開設；從零做語言模型。搜尋結果提到錄影公開在 YouTube，作業需要 GPU | [Spring 2025 課程網站](https://cs336.stanford.edu/spring2025)（另有[存檔站](https://stanford-cs336.github.io/spring2025/)） | ✅ |
| CS231n：*Convolutional Neural Networks for Visual Recognition* | 視覺方向的卷積神經網路與深度學習。搜尋結果顯示 Stanford Online 的 YouTube 有 Spring 2025 的講座（例如 *Lecture 7: Recurrent Neural Networks*）；另有說法是目前一期的錄影只給修課學生，各來源不一致 | [cs231n.stanford.edu](https://cs231n.stanford.edu) | 🔎 |
| CS229：*Machine Learning* | 機器學習。搜尋結果顯示 Andrew Ng 2018 年秋季的講座有公開錄影；`cs229.stanford.edu` 這個網域確實存在（有一份相關課程的 PDF 在它底下），但我沒有看到首頁 | [cs229.stanford.edu](https://cs229.stanford.edu) | 🔎 |
| CS25：*Transformers United* | Transformer 主題的系列課。搜尋結果列出 2021 年秋季的講座有錄影，並說可旁聽或看直播；是否仍開課請看網站 | [課程網站](https://web.stanford.edu/class/cs25/) | 🔎 |

---

## 3. 麻省理工學院（MIT）

| 課程 | 內容 | 連結 | 狀態 |
|---|---|---|---|
| 6.S191：*Introduction to Deep Learning* | MIT 的深度學習入門，由 Alexander Amini 與 Ava Soleimany 主持；講座免費公開，每年有一個頁面，我查到的存檔涵蓋 2017–2022，**最新一年我只看到 2022**，是否有更新請看網站。實驗使用 TensorFlow（依搜尋結果） | [introtodeeplearning.com](https://introtodeeplearning.com/2022)（[2021](https://introtodeeplearning.com/2021/index.html)、[2020](https://introtodeeplearning.com/2020/)） | ✅ |
| 18.06SC：*Linear Algebra*（Gilbert Strang） | OCW 的自學版線性代數；頁面列有 35 支講座影片與 36 支輔導解題影片。搜尋結果的新聞稿提到 Strang 在 2023 年春季教完最後一次 18.06 | [OCW 18.06SC](https://www.ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011) | ✅ |
| 18.065：*Matrix Methods in Data Analysis, Signal Processing, and Machine Learning* | Strang 在 2017 年開的課，講線性代數如何支撐機器學習、深度學習與神經網路；教科書是 *Linear Algebra and Learning from Data*（2019） | [OCW 18.065 課綱](https://ocw.mit.edu/courses/18-065-matrix-methods-in-data-analysis-signal-processing-and-machine-learning-spring-2018/pages/syllabus) | ✅ |

> MIT 的 6.034（人工智慧）與 6.036（機器學習導論）這次沒有查到可確認的 OCW 頁面，所以沒有列。

---

## 4. 清華大學（Tsinghua）

清華的公開課主要在**學堂在線**（XuetangX）。以下三門都是搜尋結果回傳的學堂在線頁面：

| 課程 | 內容 | 連結 | 狀態 |
|---|---|---|---|
| 大數據機器學習 | 面向資訊學科高年級本科生或研究生；統計學習基本理論、機器學習基本方法、深度學習理論與方法。主講人袁春（清華大學深圳國際研究生院）。國家高等教育智慧教育平台顯示開課平台為學堂在線，標為開課中（2026/07/23–2027/01/12） | [學堂在線](https://www.xuetangx.com/course/THU08091001026/1076286)、[智慧教育平台頁面](https://higher.smartedu.cn/course/622ac974bee70ef79f3e4f41) | ✅ |
| 深度學習訓練營 | 胡曉林副教授主講；涵蓋 NN、RNN、CNN、LSTM 等主流演算法，設計了 6 個實戰案例 | [學堂在線](https://www.xuetangx.com/course/DP08091003375/) | ✅ |
| 大數據與機器智能 | 目標是快速掌握機器學習與深度學習的基礎，並了解 AI 產業的前沿應用 | [學堂在線](https://www.xuetangx.com/course/thu08091010085/18960834) | ✅ |
| 清華 AI 素養網站 | 清華官網提到 2025 年 2 月發布；內容由校內師生講授，涵蓋生成式 AI 概念、AI 賦能教與學、倫理與責任。這個網址是官網新聞轉述的，我沒有看到頁面本身，也不確定它是否屬於公開課 | [yuketang.tsinghua.edu.cn/ai](https://yuketang.tsinghua.edu.cn/ai) | 🔎 |

> 搜尋結果也出現過「清華大模型公開課」的第三方筆記，但沒有查到官方課程頁，所以沒有列。這三門學堂在線的課是否仍開放報名，請以頁面為準。

---

## 5. 北京大學（PKU）

| 課程 | 內容 | 連結 | 狀態 |
|---|---|---|---|
| 人工智能原理 | 王文敏主講；介紹人工智能的發展歷程、核心思想、基本理論與應用。2017 年 10 月在中國大學 MOOC 首次開設，為國家精品在線開放課程；搜尋結果顯示第 14 次開課是 2024-03-18 至 2024-06-07，**已結束**，往期不提供結課證書 | [中國大學 MOOC](https://icourse163.org/course/PKU-1002188003) | ✅ |

> 北大的深度學習或大模型專門課程，這次**沒有查到**，所以沒有列。

---

## 6. 浙江大學（ZJU）

| 課程 | 內容 | 連結 | 狀態 |
|---|---|---|---|
| 人工智能：模型與算法 | 吳飛主講，為國家級首批線上一流課程；內容含邏輯推理、搜尋求解、監督學習、無監督學習、深度學習、強化學習與博弈對抗，並有以深度學習為核心的垃圾分類實訓。對應教材是高等教育出版社的《人工智能導論：模型與算法》 | [中國大學 MOOC](https://www.icourse163.org/course/ZJU-1003377027) | ✅ |
| 機器學習 | 介紹支持向量機、人工神經網路、深度學習、強化學習等模組，含 PyTorch 的程式實驗；搜尋結果摘要也提到 GAN、RNN 與 LSTM、AlphaGo 解析。主講人我沒有確認 | [中國大學 MOOC](https://www.icourse163.org/course/ZJU-1206573810) | ✅ |

> 這次沒有查到浙大專門以「大模型」為主題的 MOOC；《人工智能：模型與算法》的摘要提到「智海-三樂」這個教育垂直領域大模型，是作為教學工具出現，不是課程主題。

---

## 7. 平台入口

| 平台 | 說明 | 連結 | 狀態 |
|---|---|---|---|
| 中國大學 MOOC | 北大、浙大的課都放在這裡；搜尋「學校名稱」或教師姓名可找到更多 | [icourse163.org](https://www.icourse163.org) | ✅（課程頁所在的網站） |
| 學堂在線（XuetangX） | 清華的公開課所在平台 | [xuetangx.com](https://www.xuetangx.com) | ✅（課程頁所在的網站） |
| 國家高等教育智慧教育平台 | 彙整各校課程，搜尋結果顯示它也列有清華《大數據機器學習》 | [higher.smartedu.cn](https://higher.smartedu.cn) | ✅（課程頁所在的網站） |
| MIT OpenCourseWare | MIT 的開放課程平台 | [ocw.mit.edu](https://ocw.mit.edu) | ✅（課程頁所在的網站） |

---

## 8. 依目標選課程

![圖：六種學習目標與優先課程](figures/university-ai-courses-choose.svg)

> 這一節是我依各課程的定位做的歸納，不是學校或平台的建議。

---

## 9. 驗證說明與限制

- 驗證日期是 2026-11-17。我用網路搜尋核對課程是否存在；沙箱連不到這些學校與平台的網站，**沒有開啟任何課程頁面**，所以課程簡介取自搜尋結果的摘要。
- 標 🔎 的項目是：CS231n、CS229、CS25 的網址，與清華 AI 素養網站。前三個是各課程慣用的網址，沒有在搜尋結果裡直接看到；請自行點開確認。
- **沒有核對的內容**：各課程目前的開課學期與是否仍開放報名、哪些有完整錄影、教師與助教名單、CS224N 官方 YouTube 播放清單、CS231n 目前一期是否公開錄影、浙大《機器學習》的主講人。
- **這次沒查到、因此沒有列的課程**：北大深度學習與大模型課程、清華與浙大的大模型專門課程、MIT 6.034 與 6.036。這不代表它們不存在。
- 這份清單只涵蓋五所學校，也沒有涵蓋其他知名學校（例如 Berkeley、CMU、Harvard 的 CS50 AI）；若要擴充，請指定學校，我再查。
- 若發現連結失效或內容有誤，請在該項目標示 ⚠️ 並改為官方連結。

---

## 10. 官方來源

- 史丹佛：<https://web.stanford.edu/class/cs224n/>、<https://cs336.stanford.edu/spring2025>、<https://stanford-cs336.github.io/spring2025/>、<https://web.stanford.edu/class/cs25/>、<https://cs231n.stanford.edu>、<https://cs229.stanford.edu>
- MIT：<https://introtodeeplearning.com/2022>、<https://www.ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011>、<https://ocw.mit.edu/courses/18-065-matrix-methods-in-data-analysis-signal-processing-and-machine-learning-spring-2018/pages/syllabus>
- 清華：<https://www.xuetangx.com/course/THU08091001026/1076286>、<https://www.xuetangx.com/course/DP08091003375/>、<https://www.xuetangx.com/course/thu08091010085/18960834>、<https://higher.smartedu.cn/course/622ac974bee70ef79f3e4f41>、<https://yuketang.tsinghua.edu.cn/ai>（網址取自二手轉述）
- 北大：<https://icourse163.org/course/PKU-1002188003>
- 浙大：<https://www.icourse163.org/course/ZJU-1003377027>、<https://www.icourse163.org/course/ZJU-1206573810>
