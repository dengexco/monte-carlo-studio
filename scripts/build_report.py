from pathlib import Path
import json, os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[1]
font=os.environ.get('REPORT_FONT')
if not font:raise SystemExit('Set REPORT_FONT to a Unicode TrueType font path. Requires reportlab.')
pdfmetrics.registerFont(TTFont('Report',font))
s=json.loads((ROOT/'results/2026-10-20/results.json').read_text())
assert s['status']=='complete' and len(s['logs'])==40
styles=getSampleStyleSheet()
for name in ['Normal','Title','Heading1','Heading2']:
 styles[name].fontName='Report';styles[name].textColor=colors.HexColor('#222222')
styles['Normal'].fontSize=10;styles['Normal'].leading=15;styles['Normal'].spaceAfter=9
styles['Title'].fontSize=23;styles['Title'].leading=29;styles['Title'].alignment=0
styles['Heading1'].fontSize=16;styles['Heading1'].leading=21
styles['Heading2'].fontSize=12;styles['Heading2'].leading=17
small=ParagraphStyle('small',parent=styles['Normal'],fontSize=8,leading=12)
story=[]
def p(t):story.append(Paragraph(t,styles['Normal']))
def h(t):story.append(Paragraph(t,styles['Heading1']))
def table(rows,widths):
 t=Table(rows,colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'Report'),('FONTSIZE',(0,0),(-1,-1),8),('LEADING',(0,0),(-1,-1),11),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eceaf3')),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#dad8e0')),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),('ALIGN',(1,1),(-1,-1),'RIGHT')]));story.append(t);story.append(Spacer(1,12))
story.append(Paragraph('Monte Carlo Simulation',styles['Title']));p('Estimation of π and Euler’s number e<br/>Experiment record · 20 October 2026')
h('Purpose and setup')
p('The experiments estimate two known constants using repeated random sampling. The reference values allow the error to be measured, while five runs at each sample size show how much the estimates vary.')
table([['Setting','Value'],['Sample sizes','10, 100, 1,000, 10,000'],['Runs per sample size','5 for each experiment'],['Total estimates','40'],['Seed','20261019'],['Engine','Go PCG (math/rand/v2)']],[190,310])
h('Method for π')
p('For each run, n independent points (X, Y) are sampled uniformly in the unit square. A point is counted inside the quarter circle if X² + Y² ≤ 1. The estimate is 4 times the inside count divided by n. This follows page 62 of the lecture notes.')
h('Method for e')
p('A trial starts with sum zero and count zero. Independent uniform numbers are added until the sum is strictly greater than 1. The number of draws is recorded. Repeating this trial n times and averaging the counts gives one estimate of e. Each sample size has five complete runs. This follows page 64 of the notes.')
h('Source of the results')
p('The application was started once with the settings above. Tables use its JSON export; the two figures were downloaded through the application’s PNG buttons. CSV, JSON, run log and original PNG files are included under results/2026-10-20. No results from another seed were mixed into this record.')
story.append(Paragraph('This report and application were prepared with AI assistance. The supplied assignment prohibits AI use; this is not represented as independent student work. The PDF notes request Python, while the separately supplied instructions allow other languages. This implementation uses Go, with an optional Python launcher.',small))
for name,title,interpretation in [('pi','Pi experiment','The mean moved from 2.880000 at n=10 to 3.135920 at n=10,000. Absolute error decreased at every tested size in this run. The spread between runs also fell: sample SD changed from 0.715542 to 0.014809. The n=10 estimates ranged from 2.0 to 3.6, showing how strongly a small sample can vary.'),('e','Euler experiment','The mean moved from 2.900000 at n=10 to 2.717560 at n=10,000. Absolute error fell from 0.181718 to 0.000722. Sample SD fell from 0.412311 to 0.007466. The n=10 estimates ranged from 2.6 to 3.6; the larger sample produced a much tighter group.')]:
 story.append(PageBreak());h(title)
 rows=s['results'][name]
 table([['n','Run 1','Run 2','Run 3','Run 4','Run 5','Mean','Reference']]+[[str(r['n'])]+[f'{v:.5f}' for v in r['runs']]+[f"{r['mean']:.5f}",f"{r['reference']:.5f}"] for r in rows],[38]+[66]*7)
 table([['n','Mean','Absolute error','Sample SD']]+[[str(r['n']),f"{r['mean']:.6f}",f"{r['error']:.6f}",f"{r['sd']:.6f}"] for r in rows],[65,145,145,145])
 img=Image(str(ROOT/f'results/2026-10-20/{name}.png'));ratio=img.imageHeight/img.imageWidth;img.drawWidth=500;img.drawHeight=500*ratio;story.append(img);story.append(Spacer(1,8));story.append(Paragraph('Application export. Left: all runs, mean and reference. Right: absolute error and sample SD. Sample size and right-hand magnitude axes are logarithmic.',small));p(interpretation)
story.append(PageBreak());h('Discussion')
for title,text in [
('Which sample size had the greatest variation?','For both experiments, n=10 had the greatest sample SD: 0.715542 for π and 0.412311 for e. The smallest SD occurred at n=10,000. These statements describe this recorded run.'),
('What changed as n increased?','Both absolute error and between-run SD decreased across the four tested sizes. This supports the expected improvement in accuracy and stability, but it does not guarantee the same monotonic pattern for another seed.'),
('Why do runs with the same n differ?','Each run uses a different initialized pseudo-random stream. Different sampled points or uniform sequences give different estimates. Repeating the same complete settings reproduces the stored results.'),
('How does the Law of Large Numbers apply?','For π, the average inside-circle indicator tends toward π/4; multiplying by four gives π. For e, the average count of draws needed to exceed 1 tends toward its expectation e. Larger within-run samples reduce typical sampling variation.'),
('What would higher accuracy require?','Typical Monte Carlo standard error scales approximately as 1/√n. Halving it generally requires about four times as many trials, so more computation is needed. This is a statement about typical error, not a guarantee for one estimate.')]:
 story.append(Paragraph(title,styles['Heading2']));p(text)
h('How the statistics were calculated')
p('Mean is the average of the five estimates for one n. Absolute error is the distance from that mean to the full-precision reference constant. Sample SD uses the sum of squared deviations from the five-run mean divided by four, followed by the square root. SD is not a confidence interval. Tables show rounded numbers; calculations use the unrounded application data.')
h('References')
p('I-Stochastic Processes.pdf, Manisa Celal Bayar University, Industrial Engineering: p. 15 (Law of Large Numbers), p. 48 (simulation accuracy), pp. 61–66 (assignment methods, tables and discussion). Application source and dependency notices are included in the project package.')
def footer(c,d):
 c.setFont('Report',8);c.setFillColor(colors.HexColor('#777777'));c.drawString(47,25,'Monte Carlo Studio · 20 October 2026');c.drawRightString(548,25,str(d.page))
SimpleDocTemplate(str(ROOT/'docs/Monte-Carlo-Report.pdf'),pagesize=(595.28,841.89),rightMargin=47,leftMargin=47,topMargin=42,bottomMargin=42,title='Monte Carlo Simulation',author='').build(story,onFirstPage=footer,onLaterPages=footer)
