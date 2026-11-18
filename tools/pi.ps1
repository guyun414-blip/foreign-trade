<#
  PI 生成器：复制 原始资料/报价模板 中对应系列的模板，填入客户和报价，另存到 输出/PI/
  价格默认调用 tools/quote.mjs 计算，保证 PI 和聊天报价一致；脚本算不了的系列（Atrium、Curved）必须手动给 -UnitUsd。

  例：
    pwsh tools/pi.ps1 -Series Classic -Size 20x50 -Buyer "John" -WhatsApp "+1 555 0100" -Country "USA"
    pwsh tools/pi.ps1 -Series Transparent -Size 10x30 -Qty 2 -Buyer "Ali" -Country "Jordan" -Incoterm "CIF Aqaba" -Shipping 1300
    pwsh tools/pi.ps1 -Series Curved -Size 20x30 -UnitUsd 34.85 -Buyer "Maria"
    pwsh tools/pi.ps1 -Series Exhibition -Size 20x30 -Addon "双开玻璃门=2" -Buyer "Tom"
  不会修改模板里的银行信息。
#>
param(
  [Parameter(Mandatory)][ValidateSet('Classic','Wedding','Atrium','Transparent','Curved','Exhibition')][string]$Series,
  [Parameter(Mandatory)][string]$Size,
  [int]$Qty = 1,
  [string]$Buyer = '',
  [string]$WhatsApp = '',
  [string]$Country = '',
  [string]$Color = '',
  [string]$Incoterm = 'EXW',
  [double]$UnitUsd = 0,
  [double]$Shipping = 0,
  [string[]]$Addon = @(),
  [string]$Cbm = '',
  [string]$Weight = ''
)
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8   # Windows PowerShell 5.1 读取 node 输出需要
$Root = Split-Path $PSScriptRoot -Parent

$map = @{
  Classic     = @{ file = '1.Classic tent模板.xls';             name = 'A Shape Tent';         type = '铝合金'; color = 'White' }
  Wedding     = @{ file = '2.Wedding tent模板.xls';             name = 'Wedding Tent';         type = '铝合金'; color = 'White' }
  Atrium      = @{ file = '3.Atrium tent quotation模板.xls';    name = 'Aluminum Atrium Tent'; type = $null;    color = 'Clear PVC, Black frame' }
  Transparent = @{ file = '4.Transparent tent 模板.xls';        name = 'Transparent Tent';     type = '铝合金'; color = 'Clear PVC'; transparent = $true }
  Curved      = @{ file = '5.Curved tent quotation 模板.xls';   name = 'Curved Tent';          type = $null;    color = 'White' }
  Exhibition  = @{ file = '6.Exhibition tent quotation 模板.xls'; name = 'Exhibition Tent';    type = '铝合金'; color = 'White' }
}
$cfgS = $map[$Series]
if (-not $Color) { $Color = $cfgS.color }
if ($Size -notmatch '^\s*(\d+(?:\.\d+)?)\s*[xX*×]\s*(\d+(?:\.\d+)?)\s*$') { throw "尺寸格式应为 宽x长，如 20x50" }
$W = [double]$Matches[1]; $L = [double]$Matches[2]

# ---------- 1. 价格 ----------
$q = $null
if ($UnitUsd -le 0) {
  if (-not $cfgS.type) { throw "$Series 不在价格表中，需要人工定价：请加 -UnitUsd <美元单价/㎡>" }
  $args2 = @("$Root/tools/quote.mjs", $cfgS.type, "${W}x${L}", '--qty', $Qty, '--json')
  if ($cfgS.transparent) { $args2 += '--transparent' }
  foreach ($a in $Addon) { $args2 += @('--addon', $a) }
  $raw = & node @args2
  if ($LASTEXITCODE -ne 0) { throw "报价脚本无法计算：$raw`n→ 请人工定价后加 -UnitUsd" }
  $q = $raw | ConvertFrom-Json
}

# ---------- 2. 复制模板 ----------
$outDir = Join-Path $Root '输出/PI'
New-Item -ItemType Directory -Force $outDir | Out-Null
$safeBuyer = ($Buyer -replace '[\\/:*?"<>|\s]', '_'); if (-not $safeBuyer) { $safeBuyer = 'NoName' }
$outFile = Join-Path $outDir ("PI_{0}_{1}_{2}_{3}x{4}.xls" -f (Get-Date -Format 'yyyyMMdd-HHmm'), $safeBuyer, $Series, $W, $L)
$tpl = Join-Path $Root "原始资料/报价模板/$($cfgS.file)"
$today = Get-Date -Format 'yyyy/M/d'
$warn = @()

$xl = New-Object -ComObject Excel.Application
$xl.Visible = $false; $xl.DisplayAlerts = $false
try {
  $wb = $xl.Workbooks.Open($tpl, 0, $true)
  $wb.SaveAs($outFile, 56)   # 56 = xls
  $ws = $wb.Worksheets.Item(1)
  $cells = @($ws.UsedRange.Cells | Where-Object { $_.Text -and $_.Text.Trim() })

  function Find-Cell([string]$regex, [int]$col = 0) {
    foreach ($c in $cells) { if ((-not $col -or $c.Column -eq $col) -and $c.Text -match $regex) { return $c } }
    return $null
  }
  function Set-Label([string]$regex, [string]$value, [int]$col = 0) {
    $c = Find-Cell $regex $col; if ($c) { $c.Value2 = $value } else { $script:warn += "未找到：$regex" }
  }

  # ---------- 3. 表头 ----------
  Set-Label '^Buyer:' "Buyer: $Buyer" 1
  Set-Label '^Contact:' 'Contact:' 1
  Set-Label '^M\.P\./WhatsApp:' "M.P./WhatsApp: $WhatsApp" 1
  Set-Label '^Add:' "Add: $Country" 1
  Set-Label '^Invoice No:' ("Invoice No: GY{0}" -f (Get-Date -Format 'yyyyMMddHHmm'))
  Set-Label '^Date:' "Date: $today"
  foreach ($c in $cells) { if ($c.Text -match 'gyales6@') { $c.Value2 = $c.Value2 -replace 'gyales6@', 'sales6@' } }

  # ---------- 4. 规格表 ----------
  $item = Find-Cell '^Item$'
  if ($item) {
    $r = $item.Row; $hdr = @{}
    for ($j = 1; $j -le 12; $j++) { $t = $ws.Cells.Item($r, $j).Text.Trim(); if ($t) { $hdr[$t] = $j } }
    $vals = @{ 'Tent Size' = "${W}x${L}m"; 'Width' = "${W}m"; 'Length' = "${L}m" }
    if ($q) {
      $vals['Eave Height'] = "$($q.eave)m"; $vals['Ridge Height'] = "$($q.ridge)m"; $vals['Bay Distance'] = "$($q.bay)m"
      # 型材：基础尺寸与模板相同就保留模板原文（含壁厚），否则用价格表规格
      $cur = $ws.Cells.Item($r + 1, $hdr["Main Profile Size"]).Text
      $base = ($q.profile -replace '^(\d+\*\d+).*', '$1')
      if (-not $cur.StartsWith($base)) { $vals["Main Profile Size"] = $q.profile }
    } else { $warn += '规格表的边高/顶高/开间/型材沿用模板原值，请人工核对' }
    foreach ($k in $vals.Keys) { if ($hdr[$k]) { $ws.Cells.Item($r + 1, $hdr[$k]).Value2 = $vals[$k] } }
  } else { $warn += '未找到规格表' }

  # ---------- 5. 价格表 ----------
  $no = Find-Cell '^NO\.$'
  $sumLbl = Find-Cell '^Sum:'
  $hdr = @{}
  for ($j = 1; $j -le 12; $j++) { $t = $ws.Cells.Item($no.Row, $j).Text.Trim(); if ($t) { $hdr[$t] = $j } }
  $cN = $hdr['NAME']; $cS = $hdr['SIZE / PCS']; $cC = $hdr['COLOR']; $cQ = $hdr['QTY']
  $cA = $hdr['Covering Area']; $cU = $hdr['UNIT PRICE']; $cT = $hdr['Sub-total (USD)']
  $L1 = $no.Row + 1; $last = $sumLbl.Row - 1
  $colT = [char](64 + $cT); $colU = [char](64 + $cU); $colA = [char](64 + $cA); $colQ = [char](64 + $cQ)

  # 清空所有商品行，再写入
  for ($i = $L1; $i -le $last; $i++) { foreach ($j in @(1, $cN, $cS, $cC, $cQ, $cA, $cU, $cT)) { $ws.Cells.Item($i, $j).MergeArea.ClearContents() | Out-Null } }
  $ws.Cells.Item($L1, 1).Value2 = [double]1
  $ws.Cells.Item($L1, $cN).Value2 = $cfgS.name
  $ws.Cells.Item($L1, $cS).Value2 = "${W}x${L}m"
  $ws.Cells.Item($L1, $cC).Value2 = $Color
  $ws.Cells.Item($L1, $cQ).Value2 = [double]$Qty
  $ws.Cells.Item($L1, $cA).Formula = "=$W*$L"
  if ($q) { $ws.Cells.Item($L1, $cU).Formula = "=$($q.unitCny)/$($q.rate)" } else { $ws.Cells.Item($L1, $cU).Value2 = [double]$UnitUsd }
  $ws.Cells.Item($L1, $cT).Formula = "=$colU$L1*$colA$L1*$colQ$L1"

  # 配件行（只能用模板里的空余行）
  $row = $L1 + 1; $n = 2
  $addonList = @(); if ($q -and $q.addons) { $addonList = @($q.addons) }
  foreach ($ad in $addonList) {
    if ($row -gt $last) { $warn += "模板没有空余行，配件「$($ad.name)」请手动添加"; continue }
    $ws.Range("A$row").Value2 = [double]$n
    $ws.Cells.Item([int]$row, [int]$cN).Value2 = [string]$ad.nameEn
    if ($ad.spec) { $ws.Cells.Item([int]$row, [int]$cS).Value2 = [string]$ad.spec }
    $ws.Cells.Item([int]$row, [int]$cQ).Value2 = [double]$ad.qty
    $ws.Cells.Item([int]$row, [int]$cU).Value2 = [double]$ad.unitUsd
    $ws.Cells.Item([int]$row, [int]$cT).Formula = "=$colU$row*$colQ$row"
    $row++; $n++
  }
  if ($Addon.Count -and -not $q) { $warn += '手动定价模式不会自动填配件，请手动添加' }
  $sumCell = $ws.Cells.Item($sumLbl.Row, $cT)
  $sumCell.Formula = "=SUM($colT${L1}:$colT$last)"

  # ---------- 6. 贸易条款 / 体积 / 运费 ----------
  $tt = Find-Cell '^Trade Terms'
  if ($tt) { $ws.Cells.Item($tt.Row, $cT).Value2 = $Incoterm }
  $cbmV = if ($Cbm) { $Cbm } elseif ($q) { "$($q.cbm)" } else { '' }
  $wtV  = if ($Weight) { $Weight } elseif ($q) { "$([math]::Round($q.weightT * 1000))kg" } else { '' }
  if (-not $Cbm -or -not $Weight) { $warn += 'CBM/重量是按面积粗估的，发给客户前请核对' }
  $c = Find-Cell '^CBM:';    if ($c) { $ws.Cells.Item($c.Row, $cT).Value2 = $cbmV }
  $c = Find-Cell '^WEIGHT:'; if ($c) { $ws.Cells.Item($c.Row, $cT).Value2 = $wtV }
  $sc = Find-Cell '^Shipping cost'
  $ta = Find-Cell '^To(t)?al Amount'
  if ($ta) { $ta.Value2 = 'Total Amount:' }
  if ($sc) {
    if ($Shipping -gt 0) { $ws.Cells.Item($sc.Row, $cT).Value2 = [double]$Shipping } else { $ws.Cells.Item($sc.Row, $cT).MergeArea.ClearContents() | Out-Null }
  }
  if ($ta) {
    if ($Shipping -gt 0) { $ws.Cells.Item($ta.Row, $cT).Formula = "=$colT$($sumLbl.Row)+$colT$($sc.Row)" }
    else { $ws.Cells.Item($ta.Row, $cT).Formula = "=$colT$($sumLbl.Row)" }
  }
  if ($Incoterm -notmatch '^EXW' -and $Shipping -le 0) { $warn += "贸易术语是 $Incoterm，但没有填运费（-Shipping）" }

  # ---------- 7. 描述里的型材、备注 ----------
  if ($q -and $q.profile -match '^(\d+)\*(\d+)') {
    $new = $q.profile; $nb = "$($Matches[1])*$($Matches[2])"
    foreach ($c in $cells) {
      if ($c.Text -match 'Main profile specification|pillar:') {
        $v = [string]$c.Value2
        $v2 = [regex]::Replace($v, '\d+\*\d+(\*\d+(\.\d+)?)?mm', { param($m) if ($m.Value.StartsWith($nb + '*') -or $m.Value -eq "${nb}mm") { $m.Value } else { $new } })
        if ($v2 -ne $v) { $c.Value2 = $v2 }
      }
    }
  }
  # 非透明系列：去掉模板描述里误写的 "Transparent"（Classic 模板就写错了）
  if ($Series -in @('Classic', 'Wedding', 'Exhibition')) {
    foreach ($c in $cells) {
      if ($c.Text -match 'double-coated Transparent PVC') { $c.Value2 = ([string]$c.Value2) -replace 'double-coated Transparent PVC', 'double-coated PVC' }
    }
  }
  Set-Label '^1\.\s*Incoterms' "1. Incoterms: $Incoterm"
  Set-Label 'valid period of the offer' "3. The valid period of the offer: 15 Days from $today"

  $wb.Save()
  $total = $sumCell.Value2
  $wb.Close($false)
} catch {
  # 出错时删除半成品，避免误发一份内容仍是模板原样的 PI
  try { $wb.Close($false) } catch {}
  Remove-Item -Force -ErrorAction SilentlyContinue $outFile
  Write-Host "❌ PI 生成失败，已删除半成品：$($_.Exception.Message)"
  Write-Host $_.ScriptStackTrace
  exit 1
} finally {
  $xl.Quit() | Out-Null
  [System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) | Out-Null
}

"✅ PI 已生成：$outFile"
"   $Series ${W}x${L}m ×$Qty | 商品合计 USD {0:N2} | {1}" -f $total, $Incoterm
if ($q) { "   单价 $($q.unitCny) CNY/㎡ ÷ $($q.rate) = USD $($q.unitUsd)/㎡（$($q.match)）"; $warn += $q.warnings }
if ($warn.Count) { "⚠ " + (($warn | Select-Object -Unique) -join '；') }
"   发送前请用 Excel 打开检查一遍，模板里的图片是该系列的示意图。"
