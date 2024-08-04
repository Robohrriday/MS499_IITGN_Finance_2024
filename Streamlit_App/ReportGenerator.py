### IMPORTING LIBRARIES ###

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
# import html5lib
# from bs4 import BeautifulSoup
# import requests
# import spacy
# from nltk.tokenize import sent_tokenize
from PIL import Image
import base64

### HELPER FUNCTIONS ###

def get_base64_of_image(image_filename):
    """
    Converts an image file to a Base64 encoded data URI.
    """
    with open(image_filename, "rb") as f:
        image_data = f.read()
    encoded_data = base64.b64encode(image_data).decode()
    return f"data:image/png;base64,{encoded_data}"

### FINANCIAL ANALYSIS ###

def getSymbolReport(symbol:str, path:str = f"Streamlit_App/ReportMedia/") -> str:
    """
    Get required financial report for the desired symbol.
    symbol: Symbol
    """
    ticker = yf.Ticker(symbol)
    info_dict = ticker.get_info()
    news_list = ticker.get_news()
    institutional_holders = ticker.get_institutional_holders()
    mutualfund_holders = ticker.get_mutualfund_holders()   
    ann_income_stmt = ticker.get_income_stmt()
    qua_income_stmt = ticker.quarterly_income_stmt
    ann_balance_sheet = ticker.get_balance_sheet()
    qua_balance_sheet = ticker.quarterly_balance_sheet

    def getCompanyInfo(info_dict:dict) -> str: 

        sel_fields = ['longName','website','sector','industry','longBusinessSummary','fullTimeEmployees','companyOfficers']
        s = f"## **{info_dict['longName']}**     \n"
        for field in sel_fields:
            if field in info_dict.keys():
                if field == 'longBusinessSummary':
                    s += f"     \n### **Business Summary**     \n{info_dict[field]}"
                    continue
                elif field == 'fullTimeEmployees':
                    s += "     \n### **Employee Details**     \n"
                elif field == 'companyOfficers':
                    s += 'Major Employees:     \n'
                    for officer in info_dict['companyOfficers']:
                        s += f"- {officer['name']}: {officer['title']}     \n"
                    continue
                s += f"{field.capitalize()}: " + str(info_dict[field]) + "     \n"
        return s
    
    def getCompanyNews(news_list:list) -> str:

        sel_fields = ['title','link','publisher']
        s = f"### **Recent Company News**     \n"
        for news in news_list:
            for field in sel_fields:
                if '$' in news[field]:
                    news[field] = str.replace(news[field], '$','   \$')
                s += f"{field.capitalize()}: " + f"{news[field]}     \n"
            s += "     \n"
        return s
    
    def getInvestorData(df1:pd.DataFrame, df2:pd.DataFrame) -> str:

        # Institutional Holders and Percentage Holding
        plt.figure(figsize=(15,5))
        fig = plt.gcf()
        fig.patch.set_facecolor('#0E1117')
        plt.title(f'Institutional Holders and Percentage Holding - {symbol}', color = 'white')
        df1["shares"] = [float(i[:-1]) * 10**6 if i[-1] == "M" else float(i[:-1]) * 10**9 for i in df1["Shares"]]
        plt.pie(df1['shares'],normalize=True,labels=df1['Holder'],textprops=dict(color="w"))
        plt.pie(df1['shares'],normalize=True,labels=round((df1['shares']/df1['shares'].sum())*100,3),labeldistance=0.5,rotatelabels=True)
        plt.savefig(f'{path}Institutional_Holders_and_Percentage_Holding.png')
        
        # Mutual_Fund_Holders_and_Percentage_Holding
        plt.figure(figsize=(15,5))
        fig = plt.gcf()
        fig.patch.set_facecolor('#0E1117')
        plt.title(f'Mutual Fund Holders and Percentage Holding - {symbol}', color = 'white')
        df2["shares"] = [float(i[:-1]) * 10**6 if i[-1] == "M" else float(i[:-1]) * 10**9 for i in df2["Shares"]]
        plt.pie(df2['shares'],normalize=True,labels=df2['Holder'], textprops=dict(color="w"))
        plt.pie(df2['shares'],normalize=True,labels=round((df2['shares']/df2['shares'].sum())*100,3),labeldistance=0.5,rotatelabels=True)
        plt.savefig(f'{path}Mutual_Fund_Holders_and_Percentage_Holding.png')

        s = f"### **Investor Data**     \n![Institutional Holders and Percentage Holding]({get_base64_of_image(f'{path}Institutional_Holders_and_Percentage_Holding.png')})     \n![Mutual Fund Holders and Percentage Holding]({get_base64_of_image(f'{path}Mutual_Fund_Holders_and_Percentage_Holding.png')})     \n"
        return s
    
    def plot_current_ratio(df1:dict, df4:pd.DataFrame, df5:pd.DataFrame, ann:bool, qua:bool):
        
        columns1 = [str(column)[:10] for column in df4.columns]
        columns2 = [str(column)[:10] for column in df5.columns]

        s = ''

        if ann and qua:
            fig,ax = plt.subplots(1,2, figsize=(15,8))
            fig = plt.gcf()
            fig.patch.set_facecolor('#0E1117')
            fig.suptitle(f'Liquidity Ratio: Current Ratio - {symbol}', color = 'white')
            plt.subplots_adjust(top = 0.85)

            ax0t = ax[0].twiny()
            coords = np.arange(len(columns1))
            coords1 = coords + 0.125
            coords2 = coords - 0.125
            scaling_factor = max(np.array(df4.loc['CurrentAssets'])/np.array(df4.loc['CurrentLiabilities']))/max(np.max([np.array(df4.loc['CurrentAssets']), np.array(df4.loc['CurrentLiabilities'])], axis = 0))
            ax0t.barh(coords1, np.array(df4.loc['CurrentAssets'])*scaling_factor,0.25 , color = 'g', alpha = 0.4)
            ax0t.barh(coords2, np.array(df4.loc['CurrentLiabilities'])*scaling_factor,0.25 , color = 'r', alpha = 0.4)
            ax0t.set_xlabel(f'Downscaled Current Assets and Liablities, Scaling Factor: {scaling_factor:.3e}', color = 'white')
            ax0t.tick_params(axis='x', colors='white')

            ax[0].set_title('Annual Current Ratio', color = 'white')
            ax[0].plot(np.array(df4.loc['CurrentAssets'])/np.array(df4.loc['CurrentLiabilities']), columns1, color = 'yellow')
            ax[0].set_ylabel('Time Instance', color = 'white')
            ax[0].set_xlabel('Current Ratio', color = 'yellow')
            ax[0].grid(alpha = 0.5)
            ax[0].set_facecolor('#0e1117')
            ax[0].tick_params(axis='y', colors='white')
            ax[0].tick_params(axis='x', colors = 'yellow')

            ax0t.legend(['Current Assets', 'Current Liabilities'], loc = 'upper right')

            ax1t = ax[1].twiny()
            coords = np.arange(len(columns2))
            coords1 = coords + 0.125
            coords2 = coords - 0.125
            scaling_factor = 2/max(np.max([np.array(df5.loc['Current Assets']), np.array(df5.loc['Current Liabilities'])], axis = 0))
            ax1t.barh(coords1, np.array(df5.loc['Current Assets'])*scaling_factor,0.25 , color = 'g', alpha = 0.4)
            ax1t.barh(coords2, np.array(df5.loc['Current Liabilities'])*scaling_factor,0.25 , color = 'r', alpha = 0.4)
            ax1t.set_xlabel(f'Downscaled Current Assets and Liablities, Scaling Factor: {scaling_factor:.3e}', color = 'white')
            ax1t.legend(['Current Assets', 'Current Liabilities'], loc = 'upper right')
            ax1t.tick_params(axis='x', colors='white')

        
            ax[1].set_title('Quarterly Current Ratio', color = 'white')
            ax[1].plot( np.array(df5.loc['Current Assets'])/np.array(df5.loc['Current Liabilities']), columns2, color = 'yellow')
            ax[1].set_xlabel('Current Ratio', color = 'yellow')
            ax[1].grid(alpha = 0.5)
            ax[1].set_facecolor('#0e1117')
            ax[1].tick_params(axis='y', colors='white')
            ax[1].tick_params(axis='x', colors='yellow')

            for a in list(ax.flat) + [ax0t, ax1t]:
                a.spines['top'].set_visible(False)
                a.spines['right'].set_visible(False)
                a.spines['bottom'].set_visible(False)
                a.spines['left'].set_visible(False)

            plt.savefig(f'{path}Current_Ratio.png')

            s = f"![Current Ratio]({get_base64_of_image(f'{path}Current_Ratio.png')})     \n"
        elif ann:
            fig = plt.figure()
            fig = plt.gcf()
            fig.patch.set_facecolor('#0E1117')
            plt.title('Annual Current Ratio', color = 'white')
            plt.plot(np.array(df4.loc['CurrentAssets'])/np.array(df4.loc['CurrentLiabilities']), columns1)
            plt.ylabel('Time Instance', color = 'white')
            plt.xlabel('Current Ratio', color = 'white')
            plt.xticks(color = 'white')
            plt.yticks(color = 'white')
            plt.grid()
            plt.axis('off')
            
            s = f"![Current Ratio]({get_base64_of_image(f'{path}Current_Ratio.png')})     \n"
        elif qua:
            fig = plt.figure()
            fig = plt.gcf()
            fig.patch.set_facecolor('#0E1117')
            plt.title('Quarterly Current Ratio', color = 'white')
            plt.plot(np.array(df5.loc['CurrentAssets'])/np.array(df5.loc['CurrentLiabilities']), columns2)
            plt.ylabel('Time Instance', color = 'white')
            plt.xlabel('Current Ratio', color = 'white')
            plt.xticks(color = 'white')
            plt.yticks(color = 'white')
            plt.grid()
            plt.axis('off')

            s = f"![Current Ratio]({get_base64_of_image(f'{path}Current_Ratio.png')})     \n"
        else:
            s = f"Historical Data Unavailable. Recent Current Ratio: {df1['currentRatio']}     \n"
        return s
    
    # def plot_quick_ratio(df1:dict, df4:pd.DataFrame, df5:pd.DataFrame):
    #     fields = ['CurrentAssets', 'CurrentLiabilities','Inventory','PrepaidAssets','OtherCurrentAssets']
    #     fields1 = ['Current Assets', 'Current Liabilities','Inventory','Prepaid Assets','Other Current Assets']
    #     columns1 = [str(column)[:10] for column in df4.columns]
    #     columns2 = [str(column)[:10] for column in df5.columns]
    #     ann_quick_ratio = []
    #     qua_quick_ratio = []
    #     for index,i in enumerate(fields):
    #         if i in df4.index:
    #             ann_quick_ratio.append(index)
    #     for index,i in enumerate(fields1):
    #         if i in df5.index:
    #             qua_quick_ratio.append(index)
    #     s = ''

    #     if len(ann_quick_ratio) == 5  and len(qua_quick_ratio) == 5:
    #         fig,ax = plt.subplots(1,2,figsize=(15,8))
    #         fig.suptitle(f'Quick Ratio - {symbol}', color = 'white')
    #         fig = plt.gcf()
    #         fig.patch.set_facecolor('#0E1117')

    #         for a in ax.flat:
    #             a.spines['top'].set_visible(False)
    #             a.spines['right'].set_visible(False)
    #             a.spines['bottom'].set_visible(False)
    #             a.spines['left'].set_visible(False)

    #         ax[0].set_title('Annual Quick Ratio', color = 'white')
    #         ax[0].plot((np.array(df4.loc['CurrentAssets']) - np.array(df4.loc['Inventory']) - np.array(df4.loc['PrepaidAssets']) - np.array(df4.loc['OtherCurrentAssets']))/np.array(df4.loc['CurrentLiabilities']), columns1)
    #         ax[0].set_ylabel('Time Instance', color = 'white')
    #         ax[0].set_xlabel('Quick Ratio', color = 'white')
    #         ax[0].grid(alpha = 0.5)
    #         ax[0].set_facecolor('#0e1117')
    #         ax[0].tick_params(axis='both', colors='white')

    #         ax[1].set_xticklabels(rotation=45, labels=df5.columns[:10], color = 'white')
    #         ax[1].set_title('Quarterly Quick Ratio', color = 'white')
    #         ax[1].plot( (np.array(df5.loc['Current Assets']) - np.array(df5.loc['Inventory']) - np.array(df5.loc['Prepaid Assets']) - np.array(df5.loc['Other Current Assets']))/np.array(df5.loc['Current Liabilities']), columns2)
    #         ax[1].set_xlabel('Quick Ratio', color = 'white')
    #         ax[1].grid(alpha = 0.5)
    #         ax[1].set_facecolor('#0e1117')
    #         ax[1].tick_params(axis='both', colors='white')

    #         plt.savefig('./ReportMedia/Quick_Ratio.png')
    #         s = f"![Quick Ratio]({get_base64_of_image('./ReportMedia/Quick_Ratio.png')})     \n"

    #     elif ([i in ann_quick_ratio for i in [0,1,2,4]] == 4*[True]) and ([i in qua_quick_ratio for i in [0,1,2,4]] == 4*[True]):
    #         fig,ax = plt.subplots(1,2, figsize=(15,8))

    #         fig.suptitle(f'Quick Ratio - {symbol}', color = 'white')
    #         fig = plt.gcf()
    #         fig.patch.set_facecolor('#0E1117')

    #         for a in ax.flat:
    #             a.spines['top'].set_visible(False)
    #             a.spines['right'].set_visible(False)
    #             a.spines['bottom'].set_visible(False)
    #             a.spines['left'].set_visible(False)

    #         ax[0].set_title('Annual Quick Ratio', color = 'white')
    #         ax[0].plot((np.array(df4.loc['CurrentAssets']) - np.array(df4.loc['Inventory']) - np.array(df4.loc['OtherCurrentAssets']))/np.array(df4.loc['CurrentLiabilities']), columns1)
    #         ax[0].set_ylabel('Time Instance', color = 'white')
    #         ax[0].set_xlabel('Quick Ratio', color = 'white')
    #         ax[0].grid(alpha = 0.5)
    #         ax[0].set_facecolor('#0e1117')
    #         ax[0].tick_params(axis='both', colors='white')
            
    #         ax[1].set_title('Quarterly Quick Ratio', color = 'white')
    #         ax[1].plot((np.array(df5.loc['Current Assets']) - np.array(df5.loc['Inventory']) - np.array(df5.loc['Other Current Assets']))/np.array(df5.loc['Current Liabilities']), columns2)
    #         ax[1].set_xlabel('Quick Ratio', color = 'white')
    #         ax[1].grid(alpha = 0.5)
    #         ax[1].set_facecolor('#0e1117')
    #         ax[1].tick_params(axis='both', colors='white')

    #         plt.savefig('./ReportMedia/Quick_Ratio.png')
    #         s = f"![Quick Ratio]({get_base64_of_image('./ReportMedia/Quick_Ratio.png')})     \n"
        
    #     elif ([i in ann_quick_ratio for i in [0,1,3,4]] == 4*[True]) and ([i in qua_quick_ratio for i in [0,1,3,4]] == 4*[True]):
    #         fig,ax = plt.subplots(1,2, figsize=(15,8))
    #         fig.suptitle(f'Quick Ratio - {symbol}', color = 'white')
    #         fig = plt.gcf()
    #         fig.patch.set_facecolor('#0E1117')

    #         for a in ax.flat:
    #             a.spines['top'].set_visible(False)
    #             a.spines['right'].set_visible(False)
    #             a.spines['bottom'].set_visible(False)
    #             a.spines['left'].set_visible(False)
            
    #         ax[0].set_title('Annual Quick Ratio', color = 'white')
    #         ax[0].plot((np.array(df4.loc['CurrentAssets']) - np.array(df4.loc['PrepaidAssets']) - np.array(df4.loc['OtherCurrentAssets']))/np.array(df4.loc['CurrentLiabilities']), columns1)
    #         ax[0].set_ylabel('Time Instance', color = 'white')
    #         ax[0].set_xlabel('Quick Ratio', color = 'white')
    #         ax[0].grid(alpha = 0.5)
    #         ax[0].set_facecolor('#0e1117')
    #         ax[0].tick_params(axis='both', colors='white')


    #         ax[1].set_title('Quarterly Quick Ratio', color = 'white')
    #         ax[1].plot((np.array(df5.loc['Current Assets']) - np.array(df5.loc['Prepaid Assets']) - np.array(df5.loc['Other Current Assets']))/np.array(df5.loc['Current Liabilities']), columns2)
    #         ax[1].set_xlabel('Quick Ratio', color = 'white')
    #         ax[1].grid(alpha = 0.5)
    #         ax[1].set_facecolor('#0e1117')
    #         ax[1].tick_params(axis='both', colors='white')

    #         plt.savefig('./ReportMedia/Quick_Ratio.png')
    #         s = f"![Quick Ratio]({get_base64_of_image('./ReportMedia/Quick_Ratio.png')})     \n"

    #     elif ([i in ann_quick_ratio for i in [0,1,4]] == 4*[True]) and ([i in qua_quick_ratio for i in [0,1,4]] == 4*[True]):
    #         fig,ax = plt.subplots(1,2, figsize=(15,8))
    #         fig.suptitle(f'Quick Ratio - {symbol}', color = 'white')
    #         fig = plt.gcf()
    #         fig.patch.set_facecolor('#0E1117')

    #         for a in ax.flat:
    #             a.spines['top'].set_visible(False)
    #             a.spines['right'].set_visible(False)
    #             a.spines['bottom'].set_visible(False)
    #             a.spines['left'].set_visible(False)
            
    #         ax[0].set_title('Annual Quick Ratio', color = 'white')
    #         ax[0].plot((np.array(df4.loc['CurrentAssets']) - np.array(df4.loc['OtherCurrentAssets']))/np.array(df4.loc['CurrentLiabilities']), columns1)
    #         ax[0].set_ylabel('Time Instance', color = 'white')
    #         ax[0].set_xlabel('Quick Ratio', color = 'white')
    #         ax[0].grid(alpha = 0.5)
    #         ax[0].set_facecolor('#0e1117')
    #         ax[0].tick_params(axis='both', colors='white')

    #         ax[1].set_title('Quarterly Quick Ratio', color = 'white')
    #         ax[1].plot((np.array(df5.loc['Current Assets']) - np.array(df5.loc['Other Current Assets']))/np.array(df5.loc['Current Liabilities']), columns2)
    #         ax[1].set_xlabel('Quick Ratio', color = 'white')
    #         ax[1].grid(alpha = 0.5)
    #         ax[1].set_facecolor('#0e1117')
    #         ax[1].tick_params(axis='both', colors='white')

    #         plt.savefig('./ReportMedia/Quick_Ratio.png')
    #         s = f"![Quick Ratio]({get_base64_of_image('./ReportMedia/Quick_Ratio.png')})     \n"
        
    #     else:
    #         s = f'Historical Data Unavailable. Recent Quick Ratio: {df1['quickRatio']}     \n'
    #     return s
    
    def plot_general_financials(df1:dict, df2:pd.DataFrame, df3:pd.DataFrame, df4:pd.DataFrame, df5:pd.DataFrame):
        fig,ax = plt.subplots(2,2, figsize=(15,8), sharex = True, sharey = True)
        fig.patch.set_facecolor('#0E1117')
        fig.suptitle(f"General Annual Financials - {symbol}\nMarket Cap: \${df1['marketCap']:,} | Enterprise Value: \${df1['enterpriseValue']:,}", color = 'white')
        plt.subplots_adjust(top = 0.85)
        
        columns2 = [str(column)[:10] for column in df2.columns]
        columns3 = [str(column)[:10] for column in df3.columns]
        columns4 = [str(column)[:10] for column in df4.columns]
        columns5 = [str(column)[:10] for column in df5.columns]
        
        if 'TotalRevenue' in df2.index:
            ax[0][0].set_title('Annual Total Revenue', color = 'white')
            ax[0][0].barh(np.arange(len(df2.columns)), df2.loc['TotalRevenue'], 0.5 , color = 'g', alpha = 0.6)
            ax[0][0].grid(alpha = 0.5)
            ax[0][0].set_xlabel('Total Revenue', color = 'white')
            ax[0][0].set_ylabel('Time Instance', color = 'white')
            ax[0][0].set_yticks(np.arange(len(df2.columns)))
            ax[0][0].set_yticklabels(columns2)
            ax[0][0].tick_params(axis='both', colors='white')
            ax[0][0].set_facecolor('#0e1117')
        else:
            ax[0][0].set_title('Annual Total Revenue', color = 'white')
            ax[0][0].set_facecolor('#0e1117')
            ax[0][0].tick_params(axis='both', colors='#0e1117')
            ax[0][0].text(0.2,2, size = 15,s = "Total Revenue Data Unavailable", color = 'white')


        if 'NetIncome' in df2.index:
            ax[0][1].set_title('Annual Net Income', color = 'white')
            ax[0][1].barh(np.arange(len(df2.columns)), df2.loc['NetIncome'], 0.5 , color = 'violet', alpha = 0.6)
            ax[0][1].grid(alpha = 0.5)
            ax[0][1].set_xlabel('Net Income', color = 'white')
            ax[0][1].set_ylabel('Time Instance', color = 'white')
            ax[0][1].set_yticks(np.arange(len(df2.columns)))
            ax[0][1].set_yticklabels(columns2)
            ax[0][1].tick_params(axis='both', colors='white')
            ax[0][1].set_facecolor('#0e1117')
        else:
            ax[0][1].set_title('Annual Net Income', color = 'white')
            ax[0][1].set_facecolor('#0e1117')
            ax[0][1].tick_params(axis='both', colors='#0e1117')
            ax[0][1].text(0.2,2, size = 15,s = "Net Income Data Unavailable", color = 'white')


        if 'TotalExpenses' in df2.index:
            ax[1][0].set_title('Annual Total Expenses', color = 'white')
            ax[1][0].barh(np.arange(len(df2.columns)), df2.loc['TotalExpenses'], 0.5 , color = 'r', alpha = 0.6)
            ax[1][0].grid(alpha = 0.5)
            ax[1][0].set_xlabel('Total Expenses', color = 'white')
            ax[1][0].set_ylabel('Time Instance', color = 'white')
            ax[1][0].set_yticks(np.arange(len(df2.columns)))
            ax[1][0].set_yticklabels(columns2)
            ax[1][0].tick_params(axis='both', colors='white')
            ax[1][0].set_facecolor('#0e1117')
        else:
            ax[1][0].set_title('Annual Total Expenses', color = 'white')
            ax[1][0].set_facecolor('#0e1117')
            ax[1][0].tick_params(axis='both', colors='#0e1117')
            ax[1][0].text(0.2,2, size = 15,s = "Total Expenses Data Unavailable", color = 'white')



        if 'TotalDebt' in df4.index:
            ax[1][1].set_title('Annual Total Debt', color = 'white')
            ax[1][1].barh(np.arange(len(df4.columns)), df4.loc['TotalDebt'], 0.5 , color = 'orange', alpha = 0.6)
            ax[1][1].grid(alpha = 0.5)
            ax[1][1].set_xlabel('Total Debt', color = 'white')
            ax[1][1].set_ylabel('Time Instance', color = 'white')
            ax[1][1].set_yticks(np.arange(len(df4.columns)))
            ax[1][1].set_yticklabels(columns4)
            ax[1][1].tick_params(axis='both', colors='white')
            ax[1][1].set_facecolor('#0e1117')
        else:
            ax[1][1].set_title('Annual Total Debt', color = 'white')
            ax[1][1].set_facecolor('#0e1117')
            ax[1][1].tick_params(axis='both', colors='#0e1117')
            ax[1][1].text(0.2,2, size = 15,s = "Total Debt Data Unavailable", color = 'white')


        for a in list(ax.flat):
                a.spines['top'].set_visible(False)
                a.spines['right'].set_visible(False)
                a.spines['bottom'].set_visible(False)
                a.spines['left'].set_visible(False)
        
        plt.savefig(f'{path}General_Financials_Annual.png')

        # ax[0].set_title(f'Annual Total Revenue, Income, Expenses and Debt', color = 'white')
        # ax[0].barh(np.arange(len(df2.columns))+0.3, df2.loc['TotalRevenue'], 0.2 , color = 'g', alpha = 0.6)
        # ax[0].barh(np.arange(len(df2.columns))+0.1, df2.loc['NetIncome'], 0.2 , color = 'violet', alpha = 0.6)
        # ax[0].barh(np.arange(len(df2.columns))-0.1, df2.loc['TotalExpenses'], 0.2 , color = 'r', alpha = 0.6)
        # ax[0].barh(np.arange(len(df2.columns))-0.3, df4.loc['TotalDebt'], 0.2 , color = 'orange', alpha = 0.6)
        # ax[0].grid(alpha = 0.5)
        # ax[0].set_xlabel('Amount', color = 'white')
        # ax[0].set_ylabel('Time Instance', color = 'white')
        # ax[0].set_yticks(np.arange(len(df2.columns)))
        # ax[0].set_yticklabels(columns1)
        # ax[0].legend(['Total Revenue', 'Net Income', 'Total Expenses', 'Total Debt'])
        # ax[0].tick_params(axis='both', colors='white')
        # ax[0].set_facecolor('#0e1117')

        fig,ax = plt.subplots(2,2, figsize=(15,8), sharex = True, sharey = True)
        fig.patch.set_facecolor('#0E1117')
        fig.suptitle(f"General Quarterly Financials - {symbol}\nMarket Cap: \${df1['marketCap']:,} | Enterprise Value: \${df1['enterpriseValue']:,}", color = 'white')
        plt.subplots_adjust(top = 0.85)
        
        if 'Total Revenue' in df3.index:
            ax[0][0].set_title('Quarterly Total Revenue', color = 'white')
            ax[0][0].barh(np.arange(len(df3.columns)), df3.loc['Total Revenue'], 0.5 , color = 'g', alpha = 0.6)
            ax[0][0].grid(alpha = 0.5)
            ax[0][0].set_xlabel('Total Revenue', color = 'white')
            ax[0][0].set_ylabel('Time Instance', color = 'white')
            ax[0][0].set_yticks(np.arange(len(df3.columns)))
            ax[0][0].set_yticklabels(columns3)
            ax[0][0].tick_params(axis='both', colors='white')
            ax[0][0].set_facecolor('#0e1117')
        else:
            ax[0][0].set_title('Quarterly Total Revenue', color = 'white')
            ax[0][0].set_facecolor('#0e1117')
            ax[0][0].tick_params(axis='both', colors='#0e1117')
            ax[0][0].text(0.2,2, size = 15,s = "Total Revenue Data Unavailable", color = 'white')

        if 'Net Income' in df3.index:
            ax[0][1].set_title('Quarterly Net Income', color = 'white')
            ax[0][1].barh(np.arange(len(df3.columns)), df3.loc['Net Income'], 0.5 , color = 'violet', alpha = 0.6)
            ax[0][1].grid(alpha = 0.5)
            ax[0][1].set_xlabel('Net Income', color = 'white')
            ax[0][1].set_ylabel('Time Instance', color = 'white')
            ax[0][1].set_yticks(np.arange(len(df3.columns)))
            ax[0][1].set_yticklabels(columns3)
            ax[0][1].tick_params(axis='both', colors='white')
            ax[0][1].set_facecolor('#0e1117')
        else:
            ax[0][1].set_title('Quartery Net Income', color = 'white')
            ax[0][1].set_facecolor('#0e1117')
            ax[0][1].tick_params(axis='both', colors='#0e1117')
            ax[0][1].text(0.2,2, size = 15,s = "Net Income Data Unavailable", color = 'white')

        if 'Total Expenses' in df3.index:
            ax[1][0].set_title('Quarterly Total Expenses', color = 'white')
            ax[1][0].barh(np.arange(len(df3.columns)), df3.loc['Total Expenses'], 0.5 , color = 'r', alpha = 0.6)
            ax[1][0].grid(alpha = 0.5)
            ax[1][0].set_xlabel('Total Expenses', color = 'white')
            ax[1][0].set_ylabel('Time Instance', color = 'white')
            ax[1][0].set_yticks(np.arange(len(df3.columns)))
            ax[1][0].set_yticklabels(columns3)
            ax[1][0].tick_params(axis='both', colors='white')
            ax[1][0].set_facecolor('#0e1117')
        else:
            ax[1][0].set_title('Quarterly Total Expenses', color = 'white')
            ax[1][0].set_facecolor('#0e1117')
            ax[1][0].tick_params(axis='both', colors='#0e1117')
            ax[1][0].text(0.2,2, size = 15,s = "Total Expenses Data Unavailable", color = 'white')

        if 'Total Debt' in df5.index:
            ax[1][1].set_title('Quarterly Total Debt', color = 'white')
            ax[1][1].barh(np.arange(len(df5.columns)), df5.loc['Total Debt'], 0.5 , color = 'orange', alpha = 0.6)
            ax[1][1].grid(alpha = 0.5)
            ax[1][1].set_xlabel('Total Debt', color = 'white')
            ax[1][1].set_ylabel('Time Instance', color = 'white')
            ax[1][1].set_yticks(np.arange(len(df5.columns)))
            ax[1][1].set_yticklabels(columns5)
            ax[1][1].tick_params(axis='both', colors='white')
            ax[1][1].set_facecolor('#0e1117')
        else:
            ax[1][1].set_title('Quarterly Total Debt', color = 'white')
            ax[1][1].set_facecolor('#0e1117')
            ax[1][1].tick_params(axis='both', colors='#0e1117')
            ax[1][1].text(0.2,2, size = 15,s = "Total Debt Data Unavailable", color = 'white')


        # ax[1].set_title(f'Quarterly Total Revenue, Income, Expenses and Debt', color = 'white')
        # ax[1].barh(np.arange(len(df3.columns))+0.3, df3.loc['Total Revenue'], 0.2 , color = 'g', alpha = 0.6)
        # ax[1].barh(np.arange(len(df3.columns))+0.1, df3.loc['Net Income'], 0.2 , color = 'violet', alpha = 0.6)
        # ax[1].barh(np.arange(len(df3.columns))-0.1, df3.loc['Total Expenses'], 0.2 , color = 'r', alpha = 0.6)
        # ax[1].barh(np.arange(len(df3.columns))-0.3, df5.loc['Total Debt'], 0.2 , color = 'orange', alpha = 0.6)
        # ax[1].grid(alpha = 0.5)
        # ax[1].set_xlabel('Amount', color = 'white')
        # ax[1].set_yticks(np.arange(len(df3.columns)))
        # ax[1].set_yticklabels(columns2)
        # ax[1].legend(['Total Revenue', 'Net Income', 'Total Expenses', 'Total Debt'])
        # ax[1].tick_params(axis='both', colors='white')
        # ax[1].set_facecolor('#0e1117')

        for a in list(ax.flat):
                a.spines['top'].set_visible(False)
                a.spines['right'].set_visible(False)
                a.spines['bottom'].set_visible(False)
                a.spines['left'].set_visible(False)

        plt.savefig(f'{path}General_Financials_Quarterly.png')
        return f"![General Annual Financials]({get_base64_of_image(f'{path}General_Financials_Annual.png')}) \n![General Quarterly Financials]({get_base64_of_image(f'{path}General_Financials_Quarterly.png')}) \n"

    def plot_solvency_ratios(df4:pd.DataFrame, df5:pd.DataFrame):
        fig, ax = plt.subplots(1,2, figsize = (15, 8))
        fig.patch.set_facecolor('#0E1117')
        fig.suptitle(f'Solvency Ratios - {symbol}', color = 'white')
        columns1 = [str(column)[:10] for column in df4.columns[::-1]]
        columns2 = [str(column)[:10] for column in df5.columns[::-1]]

        ax[0].set_title('Annual Solvency Ratios', color = 'white')
        ax[0].plot(np.arange(len(columns1)), np.array(df4.loc['TotalDebt'][::-1])/np.array(df4.loc['TotalAssets'][::-1]), color = 'g', marker = 'o', alpha = 0.7)
        ax[0].plot(np.arange(len(columns1)), np.array(df4.loc['TotalDebt'][::-1])/np.array(df4.loc['StockholdersEquity'][::-1]), 'ro-', alpha = 0.7)
        ax[0].plot(np.arange(len(columns1)), np.array(df4.loc['StockholdersEquity'][::-1])/np.array(df4.loc['TotalAssets'][::-1]), color = 'orange', marker = 'o', alpha = 0.7)
        ax[0].grid(alpha = 0.5)
        ax[0].legend(['Debt-to-Asset Ratio', 'Debt-to-Equity Ratio', 'Shareholder Equity Ratio'])
        ax[0].set_xlabel('Time Instance', color = 'white')
        ax[0].set_ylabel('Ratio', color = 'white')
        ax[0].set_xticks(np.arange(len(columns1)))
        ax[0].set_xticklabels(columns1)
        ax[0].tick_params(axis='both', colors='white')
        ax[0].set_facecolor('#0e1117')

        ax[1].set_title('Quarterly Solvency Ratios', color = 'white')
        ax[1].plot(np.arange(len(columns2)), np.array(df5.loc['Total Debt'][::-1])/np.array(df5.loc['Total Assets'][::-1]), color = 'g', marker = 'o', alpha = 0.7)
        ax[1].plot(np.arange(len(columns2)), np.array(df5.loc['Total Debt'][::-1])/np.array(df5.loc['Stockholders Equity'][::-1]), 'ro-', alpha = 0.7)
        ax[1].plot(np.arange(len(columns2)), np.array(df5.loc['Stockholders Equity'][::-1])/np.array(df5.loc['Total Assets'][::-1]), color = 'orange', marker = 'o', alpha = 0.7)
        ax[1].grid(alpha = 0.5)
        ax[1].legend(['Debt-to-Asset Ratio', 'Debt-to-Equity Ratio', 'Shareholder Equity Ratio'])
        ax[1].set_xlabel('Time Instance', color = 'white')
        ax[1].set_xticks(np.arange(len(columns2)))
        ax[1].set_xticklabels(columns2)
        ax[1].tick_params(axis='both', colors='white')
        ax[1].set_facecolor('#0e1117')

        for a in list(ax.flat):
                a.spines['top'].set_visible(False)
                a.spines['right'].set_visible(False)
                a.spines['bottom'].set_visible(False)
                a.spines['left'].set_visible(False)

        plt.savefig(f'{path}Solvency_Ratios.png')
        return f"![Solvency Ratios]({get_base64_of_image(f'{path}Solvency_Ratios.png')})   \n"

    def plot_profitability_ratios(df2:pd.DataFrame, df3:pd.DataFrame, df4:pd.DataFrame, df5:pd.DataFrame):
        fig, ax = plt.subplots(1,2, figsize = (15, 8))
        fig.patch.set_facecolor('#0E1117')
        fig.suptitle(f'Profitability Ratios - {symbol}', color = 'white')
        if len(df2.columns) < len(df4.columns):
            columns1 = [str(column)[:10] for column in df2.columns[::-1]]
        else:
            columns1 = [str(column)[:10] for column in df4.columns[::-1]]
        if len(df3.columns) < len(df5.columns):
            columns2 = [str(column)[:10] for column in df3.columns[::-1]]
        else:
            columns2 = [str(column)[:10] for column in df5.columns[::-1]]

        ax[0].set_title('Annual Profitability Ratios', color = 'white')
        ax[0].plot(np.arange(len(columns1)), np.array(df2.loc['NetIncome'][::-1])/np.array(df2.loc['TotalRevenue'][::-1]), color = 'g', marker = 'o', alpha = 0.7)
        ax[0].plot(np.arange(len(columns1)), np.array(df2.loc['NetIncome'][:-min(len(df2.columns), len(df4.columns))-1:-1])/np.array(df4.loc['TotalAssets'][:-min(len(df2.columns), len(df4.columns))-1:-1]), 'ro-', alpha = 0.7)
        ax[0].plot(np.arange(len(columns1)), np.array(df2.loc['NetIncome'][:-min(len(df2.columns), len(df4.columns))-1:-1])/np.array(df4.loc['StockholdersEquity'][:-min(len(df2.columns), len(df4.columns))-1:-1]), color = 'orange', marker = 'o', alpha = 0.7)
        ax[0].grid(alpha = 0.5)
        ax[0].legend(['Net Profit Margin', 'Return On Assets (ROA)', 'Return On Equity (ROE)'])
        ax[0].set_xlabel('Time Instance', color = 'white')
        ax[0].set_ylabel('Ratio', color = 'white')
        ax[0].set_xticks(np.arange(len(columns1)))
        ax[0].set_xticklabels(columns1)
        ax[0].tick_params(axis='both', colors='white')
        ax[0].set_facecolor('#0e1117')

        ax[1].set_title('Quarterly Profitability Ratios', color = 'white')
        ax[1].plot(np.arange(len(columns2)), np.array(df3.loc['Net Income'][::-1])/np.array(df3.loc['Total Revenue'][::-1]), color = 'g', marker = 'o', alpha = 0.7)
        ax[1].plot(np.arange(len(columns2)), np.array(df3.loc['Net Income'][:-min(len(df3.columns), len(df5.columns))-1:-1])/np.array(df5.loc['Total Assets'][:-min(len(df3.columns), len(df5.columns))-1:-1]), 'ro-', alpha = 0.7)
        ax[1].plot(np.arange(len(columns2)), np.array(df3.loc['Net Income'][:-min(len(df3.columns), len(df5.columns))-1:-1])/np.array(df5.loc['Stockholders Equity'][:-min(len(df3.columns), len(df5.columns))-1:-1]), color = 'orange', marker = 'o', alpha = 0.7)
        ax[1].grid(alpha = 0.5)
        ax[1].legend(['Net Profit Margin', 'Return On Assets (ROA)', 'Return On Equity (ROE)'])
        ax[1].set_xlabel('Time Instance', color = 'white')
        ax[1].set_xticks(np.arange(len(columns2)))
        ax[1].set_xticklabels(columns2)
        ax[1].tick_params(axis='both', colors='white')
        ax[1].set_facecolor('#0e1117')

        for a in list(ax.flat):
                a.spines['top'].set_visible(False)
                a.spines['right'].set_visible(False)
                a.spines['bottom'].set_visible(False)
                a.spines['left'].set_visible(False)

        plt.savefig(f'{path}Profitability_Ratios.png')
        return f"![Profitability Ratios]({get_base64_of_image(f'{path}Profitability_Ratios.png')})  \n"
    
    def plot_earnings(df2:pd.DataFrame, df3:pd.DataFrame, df4:pd.DataFrame, df5:pd.DataFrame):
        fig, ax = plt.subplots(1,2, figsize = (15,8))
        fig.patch.set_facecolor('#0E1117')
        fig.suptitle(f'Earnings - {symbol}', color = 'white')
        columns1 = [str(column)[:10] for column in df2.columns[::-1]]
        columns2 = [str(column)[:10] for column in df3.columns[::-1]]
        plt.subplots_adjust(wspace=0.3)

        mask1 = df2.loc['BasicEPS'].isna()
        mask2 = df3.loc['Basic EPS'].isna()
        
        if "EBITDA" in df2.index and "EBIT" in df2.index and sum(df2.loc["EBITDA"].isna()) == 0 and sum(df2.loc["EBIT"].isna()) == 0: 
            ax0t = ax[0].twinx()
            scaling_factor = max(np.array(df2.loc['BasicEPS'][~mask1]))/max(max(np.array(df2.loc['EBITDA'][::-1])), max(np.array(df2.loc['EBIT'][::-1])))
            ax[0].set_title('Annual Earnings', color = 'white')
            ax[0].bar(np.arange(len(columns1)) - 0.125, np.array(df2.loc['EBITDA'][::-1])*scaling_factor,0.4, color = 'g', alpha = 0.7)
            ax[0].bar(np.arange(len(columns1)) + 0.125, np.array(df2.loc['EBIT'][::-1])*scaling_factor,0.4, color = 'violet', alpha = 0.7)
            ax0t.plot(np.arange(len(columns1)), np.array(df2.loc['BasicEPS'][::-1]), color = 'orange', marker = 'o', alpha = 0.7)
            ax0t.set_ylabel('EPS', color = 'white')
            ax[0].grid(alpha = 0.5)
            ax[0].legend(['EBITDA', 'EBIT'])
            ax[0].set_xlabel('Time Instance', color = 'white')
            ax[0].set_ylabel(f'Earnings Downscaled by {scaling_factor:.3e}', color = 'white')
            ax[0].set_xticks(np.arange(len(columns1)))
            ax[0].set_xticklabels(columns1)
            ax[0].tick_params(axis='both', colors='white')
            ax[0].set_facecolor('#0e1117')
            ax0t.tick_params(axis='y', colors='orange')

            ax0t.spines['top'].set_visible(False)
            ax0t.spines['right'].set_visible(False)
            ax0t.spines['bottom'].set_visible(False)
            ax0t.spines['left'].set_visible(False)

        elif "EBITDA" not in df2.index and "EBIT" in df2.index and sum(df2.loc["EBIT"].isna()) == 0:
            ax0t = ax[0].twinx()
            scaling_factor = max(np.array(df2.loc['BasicEPS'][~mask1]))/max(np.array(df2.loc['EBIT'][::-1]))
            ax[0].set_title('Annual Earnings', color = 'white')
            ax[0].bar(np.arange(len(columns1)), np.array(df2.loc['EBIT'][::-1])*scaling_factor,0.4, color = 'violet', alpha = 0.7)
            ax0t.plot(np.arange(len(columns1)), np.array(df2.loc['BasicEPS'][::-1]), color = 'orange', marker = 'o', alpha = 0.7)
            ax0t.set_ylabel('EPS', color = 'white')
            ax[0].grid(alpha = 0.5)
            ax[0].legend(['EBIT'])
            ax[0].set_xlabel('Time Instance', color = 'white')
            ax[0].set_ylabel(f'Earnings Downscaled by {scaling_factor:.3e}', color = 'white')
            ax[0].set_xticks(np.arange(len(columns1)))
            ax[0].set_xticklabels(columns1)
            ax[0].tick_params(axis='both', colors='white')
            ax[0].set_facecolor('#0e1117')
            ax0t.tick_params(axis='y', colors='orange')

            ax0t.spines['top'].set_visible(False)
            ax0t.spines['right'].set_visible(False)
            ax0t.spines['bottom'].set_visible(False)
            ax0t.spines['left'].set_visible(False)

        elif "EBITDA" in df2.index and "EBIT" not in df2.index and sum(df2.loc["EBITDA"].isna()) == 0:
            ax0t = ax[0].twinx()
            scaling_factor = max(np.array(df2.loc['BasicEPS'][~mask1]))/max(np.array(df2.loc['EBITDA'][::-1]))
            ax[0].set_title('Annual Earnings', color = 'white')
            ax[0].bar(np.arange(len(columns1)), np.array(df2.loc['EBITDA'][::-1])*scaling_factor,0.4, color = 'g', alpha = 0.7)
            ax0t.plot(np.arange(len(columns1)), np.array(df2.loc['BasicEPS'][::-1]), color = 'orange', marker = 'o', alpha = 0.7)
            ax0t.set_ylabel('EPS', color = 'white')
            ax[0].grid(alpha = 0.5)
            ax[0].legend(['EBITDA'])
            ax[0].set_xlabel('Time Instance', color = 'white')
            ax[0].set_ylabel(f'Earnings Downscaled by {scaling_factor:.3e}', color = 'white')
            ax[0].set_xticks(np.arange(len(columns1)))
            ax[0].set_xticklabels(columns1)
            ax[0].tick_params(axis='both', colors='white')
            ax[0].set_facecolor('#0e1117')
            ax0t.tick_params(axis='y', colors='orange')

            ax0t.spines['top'].set_visible(False)
            ax0t.spines['right'].set_visible(False)
            ax0t.spines['bottom'].set_visible(False)
            ax0t.spines['left'].set_visible(False)

        else:
            ax[0].set_title('Annual Earnings', color = 'white')
            ax[0].plot(np.arange(len(columns1)), np.array(df2.loc['BasicEPS'][::-1]), color = 'orange', marker = 'o', alpha = 0.7)
            ax[0].set_ylabel('EPS', color = 'white')
            ax[0].set_xlabel('Time Instance', color = 'white')
            ax[0].grid(alpha = 0.5)
            ax[0].set_xticks(np.arange(len(columns1)))
            ax[0].set_xticklabels(columns1)
            ax[0].tick_params(axis='x', colors='white')
            ax[0].tick_params(axis='y', colors='orange')
            ax[0].set_facecolor('#0e1117')
        

        if "EBITDA" in df3.index and "EBIT" in df3.index and sum(df3.loc["EBITDA"].isna()) == 0 and sum(df3.loc["EBIT"].isna()) == 0: 
            ax1t = ax[1].twinx()
            scaling_factor = max(np.array(df3.loc['Basic EPS'][~mask2]))/max(max(np.array(df3.loc['EBITDA'][::-1])), max(np.array(df3.loc['EBIT'][::-1])))
            ax[1].set_title('Quarterly Earnings', color = 'white')
            ax[1].bar(np.arange(len(columns2)) - 0.125, np.array(df3.loc['EBITDA'][::-1])*scaling_factor,0.4, color = 'g', alpha = 0.7)
            ax[1].bar(np.arange(len(columns2)) + 0.125, np.array(df3.loc['EBIT'][::-1])*scaling_factor,0.4, color = 'violet', alpha = 0.7)
            ax1t.plot(np.arange(len(columns2)), np.array(df3.loc['Basic EPS'][::-1]), color = 'orange', marker = 'o', alpha = 0.7)
            ax1t.set_ylabel('EPS', color = 'white')
            ax[1].grid(alpha = 0.5)
            ax[1].legend(['EBITDA', 'EBIT'])
            ax[1].set_xlabel('Time Instance', color = 'white')
            ax[1].set_ylabel(f'Earnings Downscaled by {scaling_factor:.3e}', color = 'white')
            ax[1].set_xticks(np.arange(len(columns2)))
            ax[1].set_xticklabels(columns2)
            ax[1].tick_params(axis='both', colors='white')
            ax[1].set_facecolor('#0e1117')
            ax1t.tick_params(axis='y', colors='orange')

            ax1t.spines['top'].set_visible(False)
            ax1t.spines['right'].set_visible(False)
            ax1t.spines['bottom'].set_visible(False)
            ax1t.spines['left'].set_visible(False)

        elif "EBITDA" not in df3.index and "EBIT" in df3.index and sum(df3.loc["EBIT"].isna()) == 0:
            ax1t = ax[1].twinx()
            scaling_factor = max(np.array(df3.loc['Basic EPS'][~mask2]))/max(np.array(df3.loc['EBIT'][::-1]))
            ax[1].set_title('Quarterly Earnings', color = 'white')
            ax[1].bar(np.arange(len(columns2)), np.array(df3.loc['EBIT'][::-1])*scaling_factor,0.4, color = 'violet', alpha = 0.7)
            ax1t.plot(np.arange(len(columns2)), np.array(df3.loc['Basic EPS'][::-1]), color = 'orange', marker = 'o', alpha = 0.7)
            ax1t.set_ylabel('EPS', color = 'white')
            ax[1].grid(alpha = 0.5)
            ax[1].legend(['EBIT'])
            ax[1].set_xlabel('Time Instance', color = 'white')
            ax[1].set_ylabel(f'Earnings Downscaled by {scaling_factor:.3e}', color = 'white')
            ax[1].set_xticks(np.arange(len(columns2)))
            ax[1].set_xticklabels(columns2)
            ax[1].tick_params(axis='both', colors='white')
            ax[1].set_facecolor('#0e1117')
            ax1t.tick_params(axis='y', colors='orange')

            ax1t.spines['top'].set_visible(False)
            ax1t.spines['right'].set_visible(False)
            ax1t.spines['bottom'].set_visible(False)
            ax1t.spines['left'].set_visible(False)

        elif "EBITDA" in df3.index and "EBIT" not in df3.index and sum(df3.loc["EBITDA"].isna()) == 0:
            ax1t = ax[1].twinx()
            scaling_factor = max(np.array(df3.loc['Basic EPS'][~mask2]))/max(np.array(df3.loc['EBITDA'][::-1]))
            ax[1].set_title('Quarterly Earnings', color = 'white')
            ax[1].bar(np.arange(len(columns2)), np.array(df3.loc['EBITDA'][::-1])*scaling_factor,0.4, color = 'g', alpha = 0.7)
            ax1t.plot(np.arange(len(columns2)), np.array(df3.loc['Basic EPS'][::-1]), color = 'orange', marker = 'o', alpha = 0.7)
            ax1t.set_ylabel('EPS', color = 'white')
            ax[1].grid(alpha = 0.5)
            ax[1].legend(['EBITDA'])
            ax[1].set_xlabel('Time Instance', color = 'white')
            ax[1].set_ylabel(f'Earnings Downscaled by {scaling_factor:.3e}', color = 'white')
            ax[1].set_xticks(np.arange(len(columns2)))
            ax[1].set_xticklabels(columns2)
            ax[1].tick_params(axis='both', colors='white')
            ax[1].set_facecolor('#0e1117')
            ax1t.tick_params(axis='y', colors='orange')

            ax1t.spines['top'].set_visible(False)
            ax1t.spines['right'].set_visible(False)
            ax1t.spines['bottom'].set_visible(False)
            ax1t.spines['left'].set_visible(False)

        else:
            ax[1].set_title('Quarterly Earnings', color = 'white')
            ax[1].plot(np.arange(len(columns2)), np.array(df3.loc['Basic EPS'][::-1]), color = 'orange', marker = 'o', alpha = 0.7)
            ax[1].set_ylabel('EPS', color = 'white')
            ax[1].set_xlabel('Time Instance', color = 'white')
            ax[1].grid(alpha = 0.5)
            ax[1].set_xticks(np.arange(len(columns2)))
            ax[1].set_xticklabels(columns2)
            ax[1].tick_params(axis='x', colors='white')
            ax[1].tick_params(axis='y', colors='orange')
            ax[1].set_facecolor('#0e1117')

        for a in list(ax.flat):
            a.spines['top'].set_visible(False)
            a.spines['right'].set_visible(False)
            a.spines['bottom'].set_visible(False)
            a.spines['left'].set_visible(False)

        
        plt.savefig(f'{path}Earnings.png')
        return f"![Earnings]({get_base64_of_image(f'{path}Earnings.png')}) \n"
        


    def getFinancials(df1:dict, df2:pd.DataFrame, df3:pd.DataFrame, df4:pd.DataFrame, df5:pd.DataFrame):
        sel_fields = ['totalRevenue','totalDebt','netIncome', 'totalExpense','enterpriseValue','marketCap',
                       'currentRatio', # 'quickRatio',
                       'debtToEquity', 'debtToAssets', 'equityRatio',
                       'netProfitMargin','returnOnAssets','returnOnEquity',
                       'EBITDA','EBIT', 'BasicEPS']
        s = '### **Latest Financials**  \n#### General Financials   \n'
        for field in sel_fields:
            if field == 'currentRatio':
                s += '#### Liquidity Ratios \n'
                ann_current_ratio = 0
                qua_current_ratio = 0
                if 'CurrentAssets' in df4.index and 'CurrentLiabilities' in df4.index:
                    ann_current_ratio = 1                    
                if 'Current Assets' in df5.index and 'Current Liabilities' in df5.index:
                    qua_current_ratio = 1
                
                s += plot_current_ratio(df1, df4, df5, ann_current_ratio, qua_current_ratio)
            # elif field == 'quickRatio':
            #     s += plot_quick_ratio(df1, df4, df5)
            elif field == 'totalRevenue':
                s += plot_general_financials(df1, df2, df3, df4, df5)
            elif field == 'debtToEquity':
                s += '#### Solvency Ratios  \n'
                s += plot_solvency_ratios(df4, df5)
            elif field == 'netProfitMargin':
                s += '#### Profitability Ratios \n'
                s += plot_profitability_ratios(df2, df3, df4, df5)
            elif field == 'EBITDA':
                s += '#### Earnings \n'
                s += plot_earnings(df2, df3, df4, df5)
        return s
        
    return getCompanyInfo(info_dict = info_dict) + getCompanyNews(news_list = news_list) + getInvestorData(df1 = institutional_holders, df2 = mutualfund_holders) + getFinancials(df1 = info_dict, df2 = ann_income_stmt, df3 = qua_income_stmt, df4 = ann_balance_sheet, df5 = qua_balance_sheet) 


### TECHNICAL ANALYSIS ###

def getTechnicalAnalysis(symbol:str, path:str = "Streamlit_App/"):
    """
    Get basic technical analysis for the desired symbol.
    symbol: Symbol
    """

    # Get data and process it
    
    data = yf.download(symbol, period='10y', interval='1d')
    data = data.reset_index()

    data["Date"] = pd.to_datetime(data["Date"], format="%Y-%m-%d")
    dd = data['Date'][0]

    ticker = yf.Ticker(symbol)
    actions = ticker.actions
    flag_actions = True
    if len(actions) == 0:
        flag_actions = False

    # Plot data

    recession = pd.read_csv(f"{path}GDP Based Recession Indicator.csv")    # Reference = https://fred.stlouisfed.org/series/JHGDPBRINDX
    inflation = pd.read_csv(f"{path}Inflation.csv")                        # Reference = https://fred.stlouisfed.org/series/T10YIE

    new_recession_date = pd.Series(recession['DATE'], dtype = 'datetime64[ms]')
    new_inflation_date = pd.Series(inflation['DATE'], dtype = 'datetime64[ms]')
    mask = inflation.iloc[:,1] == '.'
    new_inflation = inflation[~mask]
    new_inflation_data = pd.Series(new_inflation['T10YIE'], dtype = float)

    new_recession = pd.DataFrame({'Date':new_recession_date, 'Recession':recession.iloc[:,1]})
    new_inflation = pd.DataFrame({'Date':new_inflation_date, 'Inflation':new_inflation_data})

    for i in range(len(new_recession)):
        if new_recession.iloc[i,0].date() > dd.date():
            index = i
            break
        else:
            index = -1
    new_recession = new_recession.iloc[index:, :]

    for i in range(len(new_inflation)):
        if new_inflation.iloc[i,0].date() > dd.date():
            index = i
            break
        else:
            index = -1
    new_inflation = new_inflation.iloc[index:, :]

    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.05, subplot_titles=[f'{symbol} Stock Price','Volume Traded','GDP Based Recession Indicator (out of 100)', 'USA Breakeven Inflation Rates'])

    period = 200
    sim_mov_avg = data['Close'].rolling(window=period).mean()

    candle_trace = go.Candlestick(
        x=data["Date"],
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"],
        name = 'Price',
    ) 

    mov_avg_trace = go.Scatter(
        x=data['Date'],
        y= sim_mov_avg,
        line=dict(color="orange"),
        name=f"MA{period}"
    )

    volume_trace = go.Bar(
        x=data["Date"],
        y=data['Volume'],
        name='Volume',
        marker=dict(color='white'),
        opacity=1,  
        showlegend=True
    )

    recession_trace = go.Scatter(
        x = new_recession['Date'],
        y = new_recession['Recession'],
        name = 'USA Recession',
        showlegend = True,
        marker = dict(color='lightblue')
    )

    inflation_trace = go.Scatter(
        x = new_inflation['Date'],
        y = new_inflation['Inflation'],
        name = 'USA Inflation',
        showlegend = True,
        marker = dict(color='lightgreen')
    )


    fig.add_trace(candle_trace, row = 1, col = 1)
    fig.add_trace(mov_avg_trace, row = 1, col = 1)
    fig.add_trace(volume_trace, row = 2, col = 1)
    fig.add_trace(recession_trace, row = 3, col = 1)
    fig.add_trace(inflation_trace, row = 4, col = 1)

    if flag_actions is True:
        actions = actions.reset_index()
        actions_index_flag = True
        for i in range(len(actions)):
            if actions.iloc[i,0].date() > dd.date():
                index = i
                break
            else:
                actions_index_flag = False
                
        if actions_index_flag:
            actions = actions.iloc[index:, :]

            mask1 = actions.iloc[:,2] == 0
            mask2 = actions.iloc[:,1] == 0
            
            for i in range(len(actions[~mask1])):
                if i == len(actions[~mask1])-1:
                    date = actions.iloc[i, 0].date()
                    fig.add_vline(x=date, line_width=1, line_color="green", line_dash="solid", row = 'all', col = 'all', name = 'Stock Splits', showlegend = True)
                else:
                    date = actions.iloc[i, 0].date()
                    fig.add_vline(x=date, line_width=1, line_color="green", line_dash="solid", row = 'all', col = 'all')

            for i in range(len(actions[~mask2])):
                if i == len(actions[~mask2])-1:
                    date = actions.iloc[i, 0].date()
                    fig.add_vline(x=date, line_width=1, line_color="yellow", line_dash='dash', row = 'all', col = 'all', opacity=0.4, name = 'Dividend Payouts', showlegend = True)
                else:
                    date = actions.iloc[i, 0].date()
                    fig.add_vline(x=date, line_width=1, line_color="yellow", line_dash='dash', row = 'all', col = 'all', opacity=0.4)

    fig.update_layout(
        xaxis_rangeslider_visible = False,
        template = 'plotly_dark',
        title= f"{symbol} Chart",
        yaxis_title= "Stock Price",
        width = 2000,
        height = 2000
        # annotations=[dict(x=0.5,y=-0.03,showarrow=False,text="Date",xref="paper",yref="paper")]
    )

    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_yaxes(title_text="Indicator (out of 100)", row=3, col=1)
    fig.update_yaxes(title_text=" Inflation Rates", row=4, col=1)

    # fig.show()
    return fig


def benchmarksAndCompetitorAnalysis(symbol: str, path:str = "Streamlit_App/"):
    """
    Get comparison of returns against benchmarks and competitors from similar industry for the desired symbol.
    symbol: Symbol
    """
    # Get data and processing it
    symbol_data = yf.download(symbol, period='10y', interval='1d')
    symbol_data = symbol_data.reset_index()

    indices = {"Information Technology": "^SP500-45", "Health Care": "^SP500-35", "Financials": "^SP500-40",
               "Consumer Discretionary": "^SP500-25", "Communication Services": "^SP500-50", "Industrials": "^SP500-20",
               "Consumer Staples": "^SP500-30", "Energy": "^SP500-10", "Utilities": "^SP500-55", "Real Estate": "^SP500-60",
               "Materials": "^SP500-15", "S&P 500 Index": "^GSPC"}

    SP_data = pd.read_excel(f"{path}S&P500data.xlsx")
    SP_data.columns = SP_data.iloc[0, :]
    SP_data = SP_data.drop(index=0)

    symbol_sector = SP_data[SP_data['Symbol'] == symbol.replace("-", ".")]['GICS Sector'].item()
    symbol_subsector = SP_data[SP_data['Symbol'] == symbol.replace("-", ".")]['GICS Sub-Industry'].item()

    sector_index = yf.download(indices[symbol_sector], period='10y', interval='1d')
    sector_index = sector_index.reset_index()

    SP_index = yf.download(indices["S&P 500 Index"], period='10y', interval='1d')
    SP_index = SP_index.reset_index()

    competitor_data = SP_data[(SP_data['GICS Sector'] == symbol_sector) & (SP_data['GICS Sub-Industry'] == symbol_subsector)]
    tickers = list(competitor_data['Symbol'])
    stock_data = {}
    for ticker in tickers:
        data = yf.download(ticker, period='10y', interval='1d')
        data = data.reset_index()
        stock_data[ticker] = data

    # Plot data
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, subplot_titles=['Cumulative Returns: Stock vs Sector Index vs S&P 500','Cumulative Stock Returns: Competitor Analysis'])

    # Subplot 1: Comparison with benchmark returns
    stock_cumulative_returns = (1 + symbol_data['Adj Close'].pct_change()).cumprod()
    sector_cumulative_returns = (1 + sector_index['Adj Close'].pct_change()).cumprod()
    sp500_cumulative_returns = (1 + SP_index['Adj Close'].pct_change()).cumprod()

    stock_trace = go.Scatter(x=symbol_data['Date'], y=stock_cumulative_returns.values, mode='lines', name=competitor_data[symbol.replace("-", ".") == competitor_data['Symbol']].iloc[0,1])
    sector_trace = go.Scatter(x=sector_index['Date'], y=sector_cumulative_returns.values, mode='lines', name=symbol_sector)
    sp500_trace = go.Scatter(x=SP_index['Date'], y=sp500_cumulative_returns.values, mode='lines', name="S&P 500 Index")

    fig.add_trace(stock_trace, row=1, col=1)
    fig.add_trace(sector_trace, row=1, col=1)
    fig.add_trace(sp500_trace, row=1, col=1)

    # Subplot 2: Comparison with competitors
    for ticker in tickers:
        data = stock_data[ticker]['Adj Close']
        cumulative_returns = (1 + data.pct_change()).cumprod()
        trace = go.Scatter(x=stock_data[ticker]['Date'], y=cumulative_returns.values, mode='lines', name=competitor_data[ticker == competitor_data['Symbol']].iloc[0,1], showlegend=True)
        fig.add_trace(trace, row=2, col=1)

    fig.update_layout(title='Benchmarked Returns and Competitor Analysis', 
                      yaxis_title='Cumulative Returns (Past 10yrs)', 
                      height= 1000, template='plotly_dark',
                      yaxis2=dict(title='Cumulative Returns (Past 10yrs)'), 
                      width = 2000,
                    # annotations=[dict(x=0.5,y=-0.05,showarrow=False,text="Date",xref="paper",yref="paper")]
    )

    return fig
    

# ### WEB SCRAPING ###
# '''Credits: Nicholas Abell
# Reference: https://medium.com/@nqabell89/scraping-the-s-p-500-from-wikipedia-with-pandas-beautiful-soup-ba22101cb5ed'''

# def webScraping(symbol:str) -> None:
#     # Scrape the entire S&P500 list from Wikipedia into a Pandas DataFrame;
#     ticker_list = pd.read_html(
#     'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
#     df = ticker_list[0]

#     # Use BeautifulSoup to scrape individual wikipedia page urls for each ticker;
#     request = requests.get(
#     'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
#     df['WIKI_URL'] = ''
#     soup = BeautifulSoup(request.content)
#     main_table = soup.find(id='constituents')
#     table = main_table.find('tbody').findAll('tr')
#     table = table[1:]
#     base_url = 'https://en.wikipedia.org'
#     url_list = []
#     for item in table:
#         url = base_url + str(item.findAll('a')[1]['href'])
#         url_list.append(url)
        
#     df['WIKI_URL'] = url_list

#     url = df[df['Symbol'] == symbol]['WIKI_URL'].iloc[0]
#     response = requests.get(url)
#     soup = BeautifulSoup(response.content)

#     ### Incomplete from here.....
#     history_section = soup.find(id="History")

#     return None