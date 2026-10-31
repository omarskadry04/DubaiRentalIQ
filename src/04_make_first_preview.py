"""Static Power BI layout preview made from measured CSV values — NOT a PBIX."""
from pathlib import Path
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'data/processed'; REP=ROOT/'reports';REP.mkdir(exist_ok=True)
a=pd.read_csv(P/'fact_listing_month.csv',dtype={'listing_id':str})
b=pd.read_csv(P/'fact_peer_benchmark.csv',dtype={'listing_id':str})
c=pd.read_csv(P/'fact_coverage_month.csv')
latest=a.month_date.max();am=a[(a.month_date==latest)&(a.active)]
bm=b[b.month_date==latest];status=bm.review_signal.value_counts()
eligible=int((bm.comparison_status=='Eligible').sum());review=int(status.get('Review',0)+status.get('Large deviation',0))
zero_occ=int((am.occupancy==0).sum());total=len(am)
navy='#10253D';teal='#1B9089';amber='#DAA94D';coral='#D65B62';light='#F3F6FA';white='#FFFFFF';muted='#64758A'
fig=plt.figure(figsize=(18,10.125),facecolor=light)
def box(x,y,w,h,r=.013,color='white'):
    p=FancyBboxPatch((x,y),w,h,boxstyle=f'round,pad=.008,rounding_size={r}',facecolor=color,
                     edgecolor='#DEE5EC' if color=='white' else color,linewidth=.8,transform=fig.transFigure,zorder=0)
    fig.add_artist(p)

def label(x,y,s,size=12,col=navy,weight='normal'):
    fig.text(x,y,s,fontsize=size,color=col,fontweight=weight,fontfamily='DejaVu Sans',va='center')
box(0,0,.15,1,color=navy,r=0)
label(.022,.955,'DUBAI',21,white,'bold');label(.022,.918,'RENTAL INTELLIGENCE',9,'#DCE7F0')
for yy,tag in zip([.83,.77,.71,.65,.59,.53],['Executive overview','Trends & seasonality','Geographic intelligence','Competitive pricing','Property deep dive','Action center']):
    if yy==.83: box(.006,yy-.019,.135,.039,color='#1B486B',r=.005)
    label(.018,yy,tag,10,white if yy==.83 else '#C3D4E3','bold' if yy==.83 else 'normal')
label(.018,.15,'SOURCE',10,'#C3D4E3','bold');label(.018,.112,'AirROI sampled listings',8,white)
label(.018,.082,'Through February 2026',8,'#C3D4E3')
label(.175,.957,'DUBAI  |  Short-Term Rental Intelligence',21,navy,'bold')
label(.176,.916,'Portfolio-level observations   •   Pricing comparisons   •   Coverage-aware decisions',10,muted)
box(.836,.932,.144,.046,color='#E2ECF3',r=.01)
label(.848,.957,'Snapshot  •  FEB 2026',10,navy,'bold')
kp=[('ACTIVE SAMPLE',f'{total:,}','Listings marked active'),
    ('MEDIAN MONTHLY ADR',f'AED {am.native_avg_daily_rate.median():,.0f}','Provider-reported AED'),
    ('MEDIAN EST. OCCUPANCY',f'{am.occupancy.median():.1%}','Not verified bookings'),
    ('VALID PEER BENCHMARKS',f'{eligible:,}','10+ relevant peers')]
for j,(title,val,desc) in enumerate(kp):
    x=.175+j*.202;box(x,.788,.19,.107)
    label(x+.012,.863,title,9,muted,'bold');label(x+.012,.827,val,20,navy,'bold')
    label(x+.012,.798,desc,8,muted)
# trend rate and sample source count
box(.175,.43,.457,.333)
label(.192,.738,'Monthly median AED ADR — observed sample',13,navy,'bold')
label(.192,.710,'Rates are calculated from active listings; coverage varies by month.',8,muted)
ax=fig.add_axes([.196,.478,.413,.205])
last=c.tail(24)
ax.plot(np.arange(len(last)),last.median_active_adr_aed,color=teal,lw=2.6)
ax.fill_between(np.arange(len(last)),last.median_active_adr_aed,color=teal,alpha=.07)
ax.spines[['top','right','left']].set_visible(False);ax.spines['bottom'].set_color('#D0D9E0')
ax.tick_params(axis='both',length=0,labelsize=8,colors=muted)
ax.set_ylabel('Median AED ADR',fontsize=8,color=muted)
ax.set_xticks([0,5,11,17,23],last.month_date.iloc[[0,5,11,17,23]].str[:7].tolist())
ax.grid(axis='y',alpha=.12)
# map approximate scatter
box(.646,.43,.334,.333)
label(.664,.738,'Where the sampled listings are',13,navy,'bold')
label(.664,.71,'Coordinates are approximate; no verified neighborhood boundaries.',8,muted)
mapax=fig.add_axes([.674,.478,.28,.205]);mapax.scatter(am.longitude,am.latitude,s=6,color='#2580B2',alpha=.35,linewidths=0)
mapax.set_xlabel('Longitude',fontsize=8,color=muted);mapax.set_ylabel('Latitude',fontsize=8,color=muted)
mapax.tick_params(axis='both',labelsize=8,colors=muted)
mapax.spines[['top','right']].set_visible(False);mapax.spines[['bottom','left']].set_color('#D0D9E0')
mapax.grid(alpha=.12)
# signals
box(.175,.158,.457,.25)
label(.192,.382,'Preliminary pricing-review segmentation',13,navy,'bold')
label(.192,.357,'Heuristic rules only; a rate gap is not proof a listing is overpriced.',8,muted)
ax2=fig.add_axes([.282,.217,.325,.118])
names=['Within 20%','20–35% gap','35%+ gap','Unassessed']
nums=[int(status.get('Within threshold',0)),int(status.get('Review',0)),int(status.get('Large deviation',0)),int(status.get('Unassessed',0))]
colors=[teal,amber,coral,'#B6C5D2']
bars=ax2.barh(np.arange(4),nums,color=colors,height=.55)
ax2.set_yticks(range(4),['']*4);ax2.set_xlim(0,max(nums)*1.22)
for i,name in enumerate(names):fig.text(.193,.321 - i*.0277,name,fontsize=9,color=navy,va='center')
ax2.invert_yaxis();ax2.spines[:].set_visible(False);ax2.set_xticks([])
for i,num in enumerate(nums):ax2.text(num+12,i,f'{num:,}',va='center',fontsize=9,color=navy,fontweight='bold')
# action note
box(.646,.158,.334,.25)
label(.664,.382,'Analyst alerts',13,navy,'bold')
label(.664,.34,f'{review:,} listings flagged for manual review',12,coral,'bold')
label(.664,.304,f'{zero_occ:,} of {total:,} active listings have 0% modeled occupancy',10,navy)
label(.664,.27,f'({100*zero_occ/total:.1f}% of active records)',9,muted)
label(.664,.22,'Investigate model definitions and sample bias before',9,muted)
label(.664,.195,'drawing demand or revenue conclusions.',9,muted)
label(.175,.113,'INITIAL DATA-VALIDATED WIREFRAME  •  not a Power BI file  •  AirROI sample only',9,muted)
label(.175,.083,'Source period Mar 2021–Feb 2026 | No whole-market claims | Dashboards and DAX under development',8,muted)
output=REP/'figures/01_executive_overview_data_preview.png';output.parent.mkdir(parents=True,exist_ok=True)
fig.savefig(output,dpi=140,facecolor=fig.get_facecolor(),bbox_inches='tight',pad_inches=.1)
print('Preview:',output)
