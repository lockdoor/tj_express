document.addEventListener("DOMContentLoaded", () => {
    // --- Navigation Tabs ---
    const navButtons = document.querySelectorAll(".nav-btn");
    const tabContents = document.querySelectorAll(".tab-content");

    navButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const tabName = btn.dataset.tab;

            navButtons.forEach(b => b.classList.remove("active"));
            tabContents.forEach(c => c.classList.remove("active"));

            btn.classList.add("active");
            document.getElementById(`${tabName}-tab`).classList.add("active");
        });
    });

    // --- Dynamic Year Population ---
    const yearSelect = document.getElementById("year-select");
    const currentYearAD = new Date().getFullYear();
    const currentYearBE = currentYearAD + 543;

    // Populate past 5 years and next 1 year (e.g. 2565 to 2570)
    for (let yr = currentYearBE + 1; yr >= currentYearBE - 5; yr--) {
        const opt = document.createElement("option");
        opt.value = yr;
        opt.textContent = yr;
        if (yr === currentYearBE) {
            opt.selected = true;
        }
        yearSelect.appendChild(opt);
    }

    // --- Manual Folder Toggle ---
    const toggleManualBtn = document.getElementById("toggle-manual-btn");
    const companySelect = document.getElementById("company-select");
    const companyManual = document.getElementById("company-manual");
    let isManualMode = false;

    toggleManualBtn.addEventListener("click", () => {
        isManualMode = !isManualMode;
        if (isManualMode) {
            companySelect.removeAttribute("required");
            companySelect.parentElement.classList.add("hidden");
            companyManual.classList.remove("hidden");
            companyManual.setAttribute("required", "required");
            toggleManualBtn.textContent = "เลือกจากรายชื่อฐานข้อมูล";
        } else {
            companyManual.removeAttribute("required");
            companyManual.classList.add("hidden");
            companySelect.parentElement.classList.remove("hidden");
            companySelect.setAttribute("required", "required");
            toggleManualBtn.textContent = "พิมพ์ชื่อโฟลเดอร์เอง";
        }
    });

    // --- Config Fetching (Populate companies dropdown) ---
    const stockCompanySelect = document.getElementById("stock-company-select");
    let companiesConfig = {};

    async function loadConfig() {
        try {
            const response = await fetch("/api/v1/tax/config");
            if (!response.ok) throw new Error("โหลดข้อมูลผู้ติดต่อตั้งค่าล้มเหลว");
            const data = await response.json();

            companiesConfig = data.companies || [];

            // Populate tax dropdown
            companySelect.innerHTML = "";
            stockCompanySelect.innerHTML = "";

            if (!Array.isArray(companiesConfig) || companiesConfig.length === 0) {
                // If no preconfigured companies, force manual mode
                const emptyOpt = document.createElement("option");
                emptyOpt.value = "";
                emptyOpt.textContent = "ไม่มีการกำหนดบริษัทไว้ใน env";
                companySelect.appendChild(emptyOpt);

                // Fallback to manual
                toggleManualBtn.click();
            } else {
                companiesConfig.forEach(folder => {
                    // Tax dropdown
                    const opt = document.createElement("option");
                    opt.value = folder;
                    opt.textContent = folder;
                    companySelect.appendChild(opt);

                    // Stock dropdown
                    const sOpt = document.createElement("option");
                    sOpt.value = folder;
                    sOpt.textContent = folder;
                    stockCompanySelect.appendChild(sOpt);
                });
            }
        } catch (err) {
            console.error("Config Error:", err);
            companySelect.innerHTML = `<option value="">เกิดข้อผิดพลาดในการเชื่อมต่อ</option>`;
        }
    }

    loadConfig();

    // --- Sales Tax Report Generation ---
    const taxForm = document.getElementById("tax-form");
    const resultsPanel = document.getElementById("results-panel");
    const emptyState = document.getElementById("tax-empty-state");
    const loadingOverlay = document.getElementById("loading-overlay");
    const downloadBtn = document.getElementById("download-btn");

    const profileName = document.getElementById("profile-name");
    const profileTaxId = document.getElementById("profile-tax-id");
    const profileAddress = document.getElementById("profile-address");

    const reportTbody = document.getElementById("report-tbody");
    const totalAmountCell = document.getElementById("total-amount-cell");
    const totalVatCell = document.getElementById("total-vat-cell");

    let taxReportData = [];

    taxForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const folder = isManualMode ? companyManual.value.trim() : companySelect.value;
        const yearBE = yearSelect.value;
        const month = document.getElementById("month-select").value;

        if (!folder) {
            alert("กรุณากรอกหรือเลือกโฟลเดอร์ฐานข้อมูล");
            return;
        }

        loadingOverlay.classList.remove("hidden");

        try {
            const url = `/api/v1/tax/report?company_folder=${encodeURIComponent(folder)}&year_be=${yearBE}&month=${month}`;
            const response = await fetch(url);

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || "การดึงรายงานล้มเหลว");
            }

            const data = await response.json();
            taxReportData = data.records || [];

            // 1. Populate Profile Header
            const profile = data.company_info || {};
            profileName.textContent = profile.name || "-";

            const formattedTid = profile.tax_id ?
                `${profile.tax_id[0]}-${profile.tax_id.slice(1, 5)}-${profile.tax_id.slice(5, 10)}-${profile.tax_id.slice(10, 12)}-${profile.tax_id[12]}`
                : "-";
            profileTaxId.textContent = `เลขประจำตัวผู้เสียภาษี: ${formattedTid}`;
            profileAddress.textContent = `ที่อยู่: ${profile.address || "-"}`;

            // 2. Render Table rows
            renderTaxTable(taxReportData);

            // 3. Update summary cells
            totalAmountCell.textContent = formatCurrency(data.total_amount);
            totalVatCell.textContent = formatCurrency(data.total_vat);

            // 4. Update UI toggles
            resultsPanel.classList.remove("hidden");
            emptyState.classList.add("hidden");

            // Configure Excel Download link
            downloadBtn.classList.remove("hidden");
            downloadBtn.onclick = () => {
                window.location.href = `/api/v1/tax/download?company_folder=${encodeURIComponent(folder)}&year_be=${yearBE}&month=${month}`;
            };

        } catch (err) {
            alert(`ข้อผิดพลาด: ${err.message}`);
            resultsPanel.classList.add("hidden");
            downloadBtn.classList.add("hidden");
            emptyState.classList.remove("hidden");
        } finally {
            loadingOverlay.classList.add("hidden");
        }
    });

    // --- Search filter for Tax Table ---
    const tableSearch = document.getElementById("table-search");
    tableSearch.addEventListener("input", (e) => {
        const query = e.target.value.toLowerCase().trim();
        const filteredData = taxReportData.filter(rec => {
            return (
                rec.docnum.toLowerCase().includes(query) ||
                rec.customer_name.toLowerCase().includes(query) ||
                rec.tax_id.includes(query)
            );
        });

        renderTaxTable(filteredData);

        // Recalculate totals for the searched slice
        const subtotalAmt = filteredData.reduce((sum, r) => sum + r.amount, 0);
        const subtotalVat = filteredData.reduce((sum, r) => sum + r.vat, 0);

        totalAmountCell.textContent = formatCurrency(subtotalAmt);
        totalVatCell.textContent = formatCurrency(subtotalVat);
    });

    function renderTaxTable(records) {
        reportTbody.innerHTML = "";

        if (records.length === 0) {
            const tr = document.createElement("tr");
            tr.innerHTML = `<td colspan="9" class="text-center" style="padding: 24px; color: var(--text-secondary);">ไม่พบข้อมูลรายการภาษีขายคัดกรอง</td>`;
            reportTbody.appendChild(tr);
            return;
        }

        records.forEach(rec => {
            const tr = document.createElement("tr");

            // Format Tax ID beautifully in UI
            // Do not show Tax ID if it is 0000000000000
            const fmtTid = (tag_id) => {
                if (!tag_id || tag_id == "0000000000000") return "";
                if (tag_id.length == 13) {
                    return `${tag_id[0]}-${tag_id.slice(1, 5)}-${tag_id.slice(5, 10)}-${tag_id.slice(10, 12)}-${tag_id[12]}`;
                }
                return tag_id;
            }

            tr.innerHTML = `
                <td class="text-center">${rec.no}</td>
                <td class="text-center">${formatDate(rec.date)}</td>
                <td class="text-center font-bold">${rec.docnum}</td>
                <td>${rec.customer_name}</td>
                <td class="text-center">${fmtTid(rec.tax_id)}</td>
                <td class="text-center">${""/*rec.is_hq ? "X" : ""*/}</td>
                <td class="text-center">${""/*rec.branch_code || ""*/}</td>
                <td class="text-right ${rec.amount < 0 ? 'text-red' : ''}">${formatCurrency(rec.amount)}</td>
                <td class="text-right ${rec.vat < 0 ? 'text-red' : ''}">${formatCurrency(rec.vat)}</td>
            `;
            reportTbody.appendChild(tr);
        });
    }

    // --- Stock Count Generation ---
    const stockForm = document.getElementById("stock-form");
    const stockResultsPanel = document.getElementById("stock-results-panel");
    const stockEmptyState = document.getElementById("stock-empty-state");
    const stockTbody = document.getElementById("stock-tbody");

    let stockData = [];

    stockForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const companyId = stockCompanySelect.value;
        if (!companyId) return;

        loadingOverlay.classList.remove("hidden");

        try {
            const response = await fetch(`/api/v1/stock/${encodeURIComponent(companyId)}`);
            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || "การเรียกข้อมูลสินค้าล้มเหลว");
            }

            const data = await response.json();
            stockData = data || [];

            renderStockTable(stockData);

            stockResultsPanel.classList.remove("hidden");
            stockEmptyState.classList.add("hidden");
        } catch (err) {
            alert(`ข้อผิดพลาด: ${err.message}`);
            stockResultsPanel.classList.add("hidden");
            stockEmptyState.classList.remove("hidden");
        } finally {
            loadingOverlay.classList.add("hidden");
        }
    });

    // --- Search Filter for Stock Table ---
    const stockSearch = document.getElementById("stock-search");
    stockSearch.addEventListener("input", (e) => {
        const query = e.target.value.toLowerCase().trim();
        const filteredData = stockData.filter(item => {
            return (
                item.sku.toLowerCase().includes(query) ||
                item.name.toLowerCase().includes(query) ||
                (item.name2 && item.name2.toLowerCase().includes(query))
            );
        });
        renderStockTable(filteredData);
    });

    function renderStockTable(items) {
        stockTbody.innerHTML = "";

        if (items.length === 0) {
            const tr = document.createElement("tr");
            tr.innerHTML = `<td colspan="6" class="text-center" style="padding: 24px; color: var(--text-secondary);">ไม่พบข้อมูลสินค้าคงคลัง</td>`;
            stockTbody.appendChild(tr);
            return;
        }

        items.forEach((item, index) => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td class="text-center" style="color: var(--text-secondary);">${index + 1}</td>
                <td class="font-bold text-center">${item.sku}</td>
                <td>${item.name}</td>
                <td>${item.name2 || "-"}</td>
                <td class="text-right font-bold" style="color: #60a5fa;">${formatCurrency(item.balance)}</td>
                <td class="text-center">${item.unit || "EA"}</td>
            `;
            stockTbody.appendChild(tr);
        });
    }

    // --- Helper Formatting Utilities ---
    function formatCurrency(val) {
        if (val === undefined || val === null) return "-";
        return new Intl.NumberFormat("th-TH", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(val);
    }

    function formatDate(dateStr) {
        if (!dateStr) return "-";
        const parts = dateStr.split("-"); // YYYY-MM-DD
        if (parts.length === 3) {
            // Display as DD/MM/YYYY
            return `${parts[2]}/${parts[1]}/${parts[0]}`;
        }
        return dateStr;
    }
});
