# Phân tích & Dự đoán Hành vi Drop-off của Khách hàng trong Hành trình Mở Tài khoản Ngân hàng Số

> **G'Contest 2025 – Vòng 4 | Team: Tomorrow Data Analysts**
> Thành viên: Đinh An Khánh · Hoàng Việt Hưng · An Đức Trung

Một dự án phân tích dữ liệu end-to-end nhằm hiểu, định lượng và dự đoán hành vi **rời bỏ quy trình (drop-off)** của khách hàng khi mở tài khoản ngân hàng số (digital onboarding), từ đó đề xuất quy trình và giải pháp UI/UX mới để tăng tỷ lệ hoàn tất đăng ký.

---

## 1. Bối cảnh & Bài toán kinh doanh

Quy trình onboarding số là kênh chính để ngân hàng thu hút khách hàng mới. Tuy nhiên, một lượng khách hàng đáng kể bỏ dở giữa chừng, gây lãng phí trực tiếp chi phí thu hút khách hàng (CAC).

Phân tích trên dữ liệu **9.148 khách hàng** trong **3 tháng đầu năm 2024** cho thấy:

- Tỷ lệ mở tài khoản thành công đạt **93%** (8.543 khách thành công), nhưng tỷ lệ các phiên ở trạng thái **fail/pending chiếm tới 66,82%** và không có dấu hiệu giảm xuyên suốt 3 tháng.
- Hơn **600 khách hàng drop-off** hoàn toàn. Với CAC trung bình ~8.000.000đ (~$303) tại Đông Nam Á, tổn thất ước tính **> 4,8 tỷ đồng**.
- Hai điểm nghẽn lớn nhất là **OCR (quét giấy tờ)** và **OTP**, cùng với **Data-Privacy**, chiếm **~80%** tổng số lỗi (nguyên lý Pareto).

**Mục tiêu dự án:**
1. Dự đoán **stop-point** (điểm dừng) của khách hàng trong hành trình.
2. Tìm hiểu **nguyên nhân** dẫn đến drop-off (chia thành 2 nhóm: *trải nghiệm* và *động lực*, cùng các *yếu tố khách quan*).
3. Đề xuất **cải tiến sản phẩm/quy trình** để tăng tỷ lệ hoàn tất.

---

## 2. Dữ liệu

Nguồn dữ liệu: 1 bảng với **11 cột**, mỗi dòng là một phiên thao tác (event) của khách hàng trong hành trình onboarding.

| Cột | Mô tả | Tỉ lệ thiếu |
|---|---|---|
| `begin_time` | Thời điểm bắt đầu (string) | 0% |
| `close_time` | Thời điểm kết thúc (string) | 0% |
| `status` | Trạng thái: succeed / fail / pending | 0% |
| `gender` | Giới tính (M / F / NaN) | 41,69% |
| `birth_year` | Năm sinh | 41,37% |
| `device_type` | Loại điện thoại (Apple / Samsung / Oppo / …) | 19,73% |
| `device_system_name` | Hệ điều hành của thiết bị | 19,73% |
| `os_version` | Phiên bản hệ điều hành | 19,73% |
| `rejected_reason` | Lý do bị từ chối | 88,09% |
| `drop_off_point` | Điểm rời bỏ (7 giá trị) | 0% |
| `cus_id` | Mã khách hàng | 0% |

Hành trình onboarding gốc gồm **8 bước**: Bắt đầu → Nhập SĐT → Xác thực OTP → Đồng ý quyền riêng tư → Chụp Selfie → Đồng ý hợp đồng → Kiểm tra ngân hàng → Tạo tài khoản.

---

## 3. Quy trình thực hiện (Pipeline)

Dự án tuân theo khung **CRISP-DM**, được trình bày tuần tự trong notebook:

```
Business Understanding → Data Preparation → EDA (Situation Overview)
       → Drop-off Drivers (Statistical + ML) → Recommendation
```

### 3.1. Data Preparation — Xử lý dữ liệu thiếu & outliers

Chiến lược điền khuyết được thiết kế nhiều tầng để bảo toàn tính nhất quán của dữ liệu:

1. **Fill theo Customer ID** — Cùng một `cus_id` thường có cùng giới tính, năm sinh và loại thiết bị (chỉ 15 trường hợp thay đổi trong toàn bộ dữ liệu). Tận dụng đặc điểm này để điền khuyết theo nhóm khách hàng.
2. **Fill theo Contextual Information** — Sử dụng mối liên hệ giữa các cột (ví dụ suy luận `device_system_name`/`os_version` từ `device_type`) để điền các giá trị còn thiếu.
3. **Forward/Backward Fill** — Phần dữ liệu còn lại được điền bằng forward/backward fill để đảm bảo tính toàn vẹn.
4. `rejected_reason` được giữ nguyên (88% khuyết, không đủ thông tin để xử lý đáng tin cậy).
5. **Định dạng & xử lý outliers** — Chuyển `begin_time`/`close_time` từ string sang datetime; tính `duration`. Các giá trị bất thường (tuổi > 100, thời lượng phiên gần 50.000 phút ~ 5 tuần trong khi thực tế chỉ 5–10 phút) được thay thế bằng các chỉ số phù hợp (median theo nhóm `status`).
6. **Double-check** sau khi điền để đảm bảo phân phối dữ liệu không bị bóp méo.

### 3.2. Exploratory Data Analysis (EDA)

Phân tích chân dung khách hàng và hiệu quả hoạt động:

- **Nhân khẩu học:** Khách hàng chủ yếu là **Gen Y (25–35 tuổi)** — nhóm bắt đầu ổn định tài chính; nữ giới chiếm ưu thế nhẹ (57,8%).
- **Thiết bị:** **>80% dùng Apple** với phiên bản OS mới nhất → gợi ý ưu tiên tối ưu trên iOS.
- **Hành vi thời gian:** Tập trung vào giờ hành chính, các ngày trong tuần, đột biến mạnh sau Tết Nguyên đán (29/2 – 1/3).
- **Phân tích lỗi:** Pareto chart xác định OTP/OCR/Data-Privacy là nhóm điểm dừng nghiêm trọng nhất; OCR có tỷ lệ **lặp lại lỗi** cao nhất (khách hàng bị mắc kẹt, thử nhiều lần).

### 3.3. Feature Engineering

Từ **8 biến gốc**, tạo ra **19 biến mới** chia thành 3 nhóm:

| Nhóm | Biến |
|---|---|
| **Đặc điểm khách hàng** (4) | `age`, `gender_M`, `phone_type_X` (one-hot) |
| **Hành vi khách hàng** (6) | `cumulative_attempts`, `total_past_fail`, `total_past_pending`, `fail_pending_count_X` |
| **Bối cảnh thao tác** (9) | `hour_of_day`, `day_of_week`, `is_weekend`, `is_office_hour`, `time_X` (morning/evening) |

---

## 4. Phương pháp phân tích

Dự án kết hợp cả **thống kê suy luận** và **học máy** để đảm bảo kết luận vững chắc:

### 4.1. Kiểm định Chi-square
Kiểm tra mối liên hệ giữa `age_group`/`phone_type` với lỗi OTP và OCR. Kết quả cho thấy **age_group có ý nghĩa thống kê rất mạnh** (p ≈ 0) với cả hai loại lỗi → độ tuổi là yếu tố thực sự liên quan.

### 4.2. Survival Analysis
Sử dụng thư viện **`lifelines`** để mô hình hóa "khả năng sống sót" (tiếp tục thử lại) của khách hàng theo số lần thử:
- **Kaplan-Meier** so sánh đường cong thành công giữa các nhóm (thế hệ, thiết bị, buổi trong ngày, giới tính, cuối tuần).
- **Log-rank test** kiểm định sự khác biệt giữa các nhóm.
- **Cox Proportional Hazards Regression** định lượng tác động (hazard ratio) của từng yếu tố.

> **Insight chính:** *Thế hệ* là yếu tố khác biệt lớn nhất (Boomers có tỷ lệ thành công thấp, cần nhiều lần thử hơn). Thực hiện vào *buổi sáng/tối* tăng khả năng thành công; thiết bị *Redmi/Others* làm giảm. *Giới tính* và *cuối tuần* không có tác động đáng kể.

### 4.3. Predictive Modeling

Hai bài toán mô hình hóa riêng biệt:

**Mô hình 1 — Dự đoán drop-off ở lần thử cuối cùng**
- Lấy bản ghi cuối cùng của mỗi khách hàng làm dữ liệu huấn luyện; 19 biến đầu vào.
- Target: `drop_off = 1` nếu khách hàng không hoàn tất quy trình, `0` nếu thành công.

**Mô hình 2 — Dự đoán fail tại từng bước**
- Mỗi bước (OTP, Data-Privacy, OCR, Selfie, Contract, Bank-check) có một mô hình riêng; 12 biến đầu vào.
- Target: `fail_step = 1` nếu fail ở bước đó.

**Kỹ thuật chung:**
- **SMOTE** (oversampling) xử lý mất cân bằng dữ liệu, đặt trong `imblearn.Pipeline` để tránh data leakage.
- So sánh 3 thuật toán: **XGBoost**, **LightGBM**, **Random Forest**.
- Tối ưu siêu tham số bằng **RandomizedSearchCV**; kiểm định chéo phân tầng (**StratifiedKFold** + `cross_validate`).
- Metric chính: **ROC-AUC** (kèm Accuracy, F1, Precision, Recall).
- Giải thích mô hình bằng **Feature Importance** và **biểu đồ SHAP**.

---

## 5. Kết quả

### Mô hình 1 — Drop-off prediction (Cross-validation)

| Metric | **XGBoost** ✅ | LightGBM | Random Forest |
|---|---|---|---|
| **ROC-AUC** | **0.8943** | 0.8927 | 0.8907 |
| Accuracy | 0.9287 | 0.9303 | 0.9351 |
| F1 | 0.5462 | 0.5442 | 0.5255 |
| Precision | 0.4742 | 0.4808 | 0.5100 |
| Recall | 0.6463 | 0.6281 | 0.5438 |

→ Chọn **XGBoost** (ROC-AUC cao nhất). Phân tích Feature Importance + SHAP cho thấy `age`, `gender_M`, và lịch sử lỗi quá khứ (`fail_pending_count_*` tại Contract, OCR, Check, OTP) cùng `cumulative_attempts` là các yếu tố quyết định mạnh nhất đến hành vi rời bỏ.

### Mô hình 2 — Fail prediction theo từng bước

| Metric | OTP (XGB) | Data-Privacy (XGB) | OCR (RF) | Selfie (LGBM) | Contract (LGBM) | Bank-check (RF) |
|---|---|---|---|---|---|---|
| ROC-AUC | 0.6346 | 0.6048 | 0.5802 | 0.5536 | 0.6821 | 0.5985 |

> **Tính trung thực trong báo cáo:** Nhóm chủ động chỉ ra rằng ROC-AUC của các mô hình bước chỉ dao động quanh 0.5–0.6 (≈ đoán ngẫu nhiên), do đó kết luận rằng các mô hình này **chưa đủ độ tin cậy** và feature importance chỉ mang tính tham khảo — thay vì cường điệu kết quả.

---

## 6. Đề xuất (Recommendation)

Trên cơ sở phân tích + benchmark 10 ngân hàng lớn tại Việt Nam (đối chiếu khảo sát FICO 2021, Capgemini 2024, FPT.AI), nhóm đề xuất 3 hướng:

1. **Tối ưu quy trình mở tài khoản** — Chuẩn hóa thành **9 bước cốt lõi**, gộp đồng ý quyền riêng tư vào nút "Tiếp tục", thay **chụp CCCD bằng quét QR chip** (giảm tỷ lệ lỗi OCR từ ~20% xuống ~6%), auto-fill OTP, đếm ngược ký tự SĐT, bổ sung xác thực **VNeID** thay NFC cho thiết bị không hỗ trợ.
2. **Tăng động lực** — Quà tặng khi mở tài khoản, ưu đãi giới thiệu bạn bè, hợp tác KOL/người nổi tiếng (vì >1/3 khách rời bỏ ngay lần thử đầu tiên → động lực chưa đủ lớn).
3. **Hỗ trợ yếu tố khách quan** — Chatbot tự động khi khách dừng quá lâu/fail 2 lần, ghi nhận SĐT sớm để CSKH chủ động tiếp cận, hướng dẫn giải pháp thay thế (đăng ký tại quầy).

**Đo lường:** Đề xuất triển khai **A/B Testing** (nhóm control vs treatment) + **Hypothesis Testing** (t-test / chi-square) để đánh giá khách quan.

**Kỳ vọng:** Tỷ lệ thành công 93% → **>97%**; giảm đáng kể tỷ lệ fail của nhóm Baby Boomers (~39%).

---

## 7. Công nghệ sử dụng

| Hạng mục | Công cụ |
|---|---|
| Ngôn ngữ | Python 3 |
| Xử lý dữ liệu | `pandas`, `numpy` |
| Trực quan hóa | `matplotlib`, `seaborn` |
| Học máy | `scikit-learn`, `xgboost`, `lightgbm` |
| Mất cân bằng dữ liệu | `imbalanced-learn` (SMOTE) |
| Giải thích mô hình | `shap` |
| Phân tích sống còn | `lifelines` (Kaplan-Meier, Cox PH, log-rank) |
| Môi trường | Google Colab / Jupyter Notebook |

---

## 8. Cấu trúc dự án

```
.
├── code.ipynb     # Notebook end-to-end: Data Prep → EDA → Feature Eng → Modeling → Survival Analysis
├── slide.pdf      # Slide trình bày kết quả (G'Contest 2025)
└── README.md
```

---

## 9. Điểm nổi bật về kỹ năng

- **Tư duy kinh doanh:** Quy đổi vấn đề kỹ thuật ra tác động tài chính (tổn thất 4,8 tỷ đồng theo CAC) và đề xuất hành động cụ thể, có thể triển khai.
- **Xử lý dữ liệu thực tế:** Chiến lược điền khuyết nhiều tầng dựa trên hiểu biết về dữ liệu (theo `cus_id`, theo context) thay vì điền máy móc.
- **Phương pháp đa dạng & phù hợp:** Kết hợp kiểm định thống kê (Chi-square, log-rank), phân tích sống còn (Cox), và ML có giải thích (SHAP) — không chỉ dừng ở "train một model".
- **Kỹ thuật ML chuẩn:** SMOTE đặt trong pipeline tránh leakage, tuning + cross-validation, so sánh nhiều thuật toán theo metric phù hợp với dữ liệu mất cân bằng (ROC-AUC).
- **Tính trung thực khoa học:** Thẳng thắn chỉ ra giới hạn của mô hình bước (ROC-AUC ~0.6) và không kết luận quá mức.

---

## 10. Tài liệu tham khảo

- FPT.AI (2022) — *eKYC adoption at Vietnam's commercial banks*
- Capgemini (2024) — *Bank onboarding completion rates*
- FICO (2021) / Vietnam News — *Two out of five Vietnamese consumers abandon long online banking applications*
- CCG Catalyst (2024) — *How AI can speed bank onboarding and reduce abandonment*
- SalesWorks Group — *Customer Acquisition Cost in Southeast Asia*
