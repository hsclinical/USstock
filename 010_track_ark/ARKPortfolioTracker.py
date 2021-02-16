#!/usr/bin/python3

"""
ARKPortfolioTracker.py

    Author: Hong Lu (luhongisu@gmail.com)
    Last Update: 2021/02/13
    Current Version: v1.0.0

    Decription:
        This is a script to download and track ARK stock data every workday

    Example:
    $ python ARKPortfolioTracker.py -o YourDataFolder

    Crontab to execute (Every weekday @ 9:00PM)
    $ 0 21 * * 1-5 python ARKPortfolioTracker.py -o YourDataFolder

    Log:
    v1.0.0, Date: Feb 13, 2021
        Initate the script

    Reference:
    1. Gmail SMTP login error (https://stackoverflow.com/questions/16512592/login-credentials-not-working-with-gmail-smtp)
"""
import argparse, os, sys, logging, datetime, smtplib
from os import path
from urllib.request import Request, urlopen
from shutil import copyfileobj

# Section - Log
pdLogger = logging.getLogger('pdLogger')
formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
pdLogger.setLevel(logging.INFO)

# Section - Class
class ARKPortfolioTracker(object):
    def __init__(self, args):
        self.output_dir = args.output_dir

        # set up logging
        pdOutHandler = logging.FileHandler( os.path.join(self.output_dir, 'stdout.log') )
        pdOutHandler.setLevel(logging.INFO)
        pdOutHandler.setFormatter(formatter)

        pdErrHandler = logging.FileHandler( os.path.join(self.output_dir, 'stderr.err'))
        pdErrHandler.setLevel(logging.ERROR)
        pdErrHandler.setFormatter(formatter)

        pdLogger.addHandler(pdOutHandler)
        pdLogger.addHandler(pdErrHandler)

        # set up download link
        self.PDFLink = {}
        # ARKK: ARK INNOVATION ETF
        self.PDFLink[ 'ARKK' ] = 'https://ark-funds.com/wp-content/fundsiteliterature/holdings/ARK_INNOVATION_ETF_ARKK_HOLDINGS.pdf'
        # ARK Autonomous Technology & Robotics ETF
        self.PDFLink[ 'ARKQ' ] = 'https://ark-funds.com/wp-content/fundsiteliterature/holdings/ARK_AUTONOMOUS_TECHNOLOGY_&_ROBOTICS_ETF_ARKQ_HOLDINGS.pdf'
        # ARK Next Generation Internet ETF
        self.PDFLink[ 'ARKW' ] = 'https://ark-funds.com/wp-content/fundsiteliterature/holdings/ARK_NEXT_GENERATION_INTERNET_ETF_ARKW_HOLDINGS.pdf'
        # ARK Genomic Revolution ETF
        self.PDFLink[ 'ARKG' ] = 'https://ark-funds.com/wp-content/fundsiteliterature/holdings/ARK_GENOMIC_REVOLUTION_MULTISECTOR_ETF_ARKG_HOLDINGS.pdf'
        # ARK FINTECH INNOVATION ETF
        self.PDFLink[ 'ARKF' ] = 'https://ark-funds.com/wp-content/fundsiteliterature/holdings/ARK_FINTECH_INNOVATION_ETF_ARKF_HOLDINGS.pdf'

        # set up email
        self.gmailUser = 'YourFromEmail'
        self.gmailPassword = 'YourPassword'

        self.to = [ 'YourToEmail' ]
        self.subject = 'ARK download'
        self.body = ''


    def downloadPDFFile(self, curTimeStr):
        for ETFName in self.PDFLink:
            try:
                outDir = os.path.join(self.output_dir, ETFName, '')
                pdLogger.info('Download (success) ' + ETFName + ' to ' + outDir)
                self.body += 'Download (success) ' + ETFName + ' to ' + outDir + '\n'
                if not os.path.exists(outDir):
                    os.makedirs(str(outDir))
                req = Request(self.PDFLink[ ETFName ], headers={'User-Agent': 'Mozilla/5.0'})
                with urlopen(req ) as in_stream, open(os.path.join(self.output_dir, ETFName, ETFName + '_' + curTimeStr + '.pdf'), 'wb') as out_file:
                    copyfileobj(in_stream, out_file)
            except Exception:
                pdLogger.error('Download (fail)' + ETFName, exc_info=True)
                self.body += 'Download (fail)' + ETFName + '\n'
        pdLogger.info('Download complete')
        self.body += 'Download complete'


    def sendEmailNotice(self, curTimeStr):
        self.subject += ' - ' + curTimeStr
        self.emailText ="""\
From: %s
To: %s
Subject: %s

%s
""" % (self.gmailUser, ", ".join(self.to), self.subject, self.body)

        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(self.gmailUser, self.gmailPassword)
            server.sendmail(self.gmailUser, self.to, self.emailText)
            server.close()

            pdLogger.info('Email sent\n\n')
        except Exception:
            pdLogger.error('Email sent (fail)', exc_info=True)
            pdLogger.error('\n\n')


    def main(self):
        curTimeObj = datetime.datetime.now()
        curTimeStr = curTimeObj.strftime('%Y%m%d-%a')

        self.downloadPDFFile(curTimeStr)
        self.sendEmailNotice(curTimeStr)


# Section - To parse and check agrv
if __name__ == '__main__':  
    parser = argparse.ArgumentParser(description='Parameters for ARKPortfolioTracker.py')
    parser.add_argument('-o', '--output_dir', help = 'Output Folder', type = str, required=True)

    args = parser.parse_args()
    apt = ARKPortfolioTracker(args)
    apt.main()