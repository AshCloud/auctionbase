# parser.py


import datetime
import locale
import sys
import xml.dom.minidom


#Initialize user list. This will be used to keep track of bidders, sellers and bidder/sellers and making sure there are no duplicates
users = []

def transform_dollar(dollar_str):
    """
    Returns the amount (in XXXXX.xx format) denoted by a money-string
    like $3,453.23. 
    """
    return '{:.2f}'.format(locale.atof(dollar_str.strip("$")))

def transform_dttm(dttm_str):
    """
    Returns date/time string in format like "2001-03-25 10:25:57" from
    a format like "Mar-25-01 10:25:57".
    """
    dt = datetime.datetime.strptime(dttm_str, "%b-%d-%y %H:%M:%S")  
    return dt.isoformat(' ')

def writeItem(item):
    """
    Extract the Items from the XML file and all attributes and write them to the itemfile (item.dat)
    """
    line = ""
    
    itemID = item.getAttribute('ItemID')
    line = line + str(itemID)
    
    namelist = item.getElementsByTagName('Name')
    for n in namelist:
        name = n.firstChild.data
        line = line + "|" + str(name)
    
    currentlylist = item.getElementsByTagName('Currently')
    for c in currentlylist:
        currently = transform_dollar(c.firstChild.data)
        line = line + "|" + str(currently)
    
    buypricelist = item.getElementsByTagName('Buy_Price')
    if len(buypricelist) < 1:
        line = line + "|" + " "
    for b in buypricelist:
        buy_price = transform_dollar(b.firstChild.data)
        line = line + "|" + str(buy_price)
    
    firstbidlist = item.getElementsByTagName('First_Bid')
    for f in firstbidlist:
        first_bid = transform_dollar(f.firstChild.data)
        line = line + "|" + str(first_bid)
    
    numofbidslist = item.getElementsByTagName('Number_of_Bids')
    for nb in numofbidslist:
        num_of_bids = nb.firstChild.data
        line = line + "|" + str(num_of_bids)
    
    startedlist = item.getElementsByTagName('Started')
    for s in startedlist:
        started = transform_dttm(s.firstChild.data)
        line = line + "|" + str(started)
    
    endslist = item.getElementsByTagName('Ends')
    for e in endslist:
        ends = transform_dttm(e.firstChild.data)
        line = line + "|" + str(ends)
    
    sellerIDlist = item.getElementsByTagName('Seller')
    for s in sellerIDlist:
        sellerID = s.getAttribute('UserID')
        line = line +  "|" + str(sellerID)
    
    descriptionlist = item.getElementsByTagName('Description')
    for d in descriptionlist:
        if str(d.firstChild) == 'None':
            line = line + "|" + " "
        else:
            description = str(d.firstChild.data)
            line = line + "|" + description
    
    itemfile = open('item.dat', 'a')
    itemfile.write(line + "\n")
    itemfile.close()

def writeUser(item, userID):
    """
    Extract the Bidders/Sellers from the XML file and all attributes and write them to the bidderfile (bidder.dat)
    """

    line = "" + userID

    BidderList = item.getElementsByTagName('Bidder')
    if len(BidderList) > 0:
        rating = item.getElementsByTagName('Bidder')[0].getAttribute('Rating')
        line = line + "|" + str(rating)       
    
    location = item.getElementsByTagName('Location')[0].firstChild.data
    if location == " ":
        line = line + "|" + " "
    else:
        line = line + "|" + str(location)
    
    country = item.getElementsByTagName('Country')[0].firstChild.data
    if country == " ":
        line = line + "|" + " "
    else:
        line = line + "|" + str(country)

    userfile = open('user.dat', 'a')
    userfile.write(line + "\n")
    userfile.close()
    

def writeBid(item):
    """
    Extract the Bids from the XML file and all attributes and write them to the bidfile (bid.dat)
    """
    line = ""

    itemID = item.getAttribute('ItemID')
    line = line + str(itemID)

    userID = item.getElementsByTagName('Bidder')[0].getAttribute('UserID')
    line = line + "|" + str(userID)
            
    timelist = item.getElementsByTagName('Time')
    for t in timelist:
        time = transform_dttm(t.firstChild.data)
    line = line + "|" + str(time)

    amountlist = item.getElementsByTagName('Amount')
    for a in amountlist:
        amount = transform_dollar(a.firstChild.data)
    line = line + "|" + str(amount)

    bidfile = open('bid.dat', 'a')
    bidfile.write(line + "\n")
    bidfile.close()
    
def writeCategory(item):
    """Category Relation"""
    line = ""
    
    itemID = item.getAttribute('ItemID')
    line = line + str(itemID)
        
    categorylist = item.getElementsByTagName('Category')
    for c in categorylist:
        category = c.firstChild.data
        line = line + "|" + str(category)

    categoryfile = open('category.dat', 'a')
    categoryfile.write(line + "\n")
    categoryfile.close()    

def process_file(filename):
    """
    Process one items-???.xml file.
    """
    dom = xml.dom.minidom.parse(filename)

    Items = dom.getElementsByTagName('Item')

    for item in Items:   

        # Write tuple into Item table
        writeItem(item)

        # Keep track of previously encountered bidders/sellers by storing them in a list to avoid duplicates. Only want each seller posted once.
        sellerIDlist = item.getElementsByTagName('Seller')
        for s in sellerIDlist:
            sellerID = s.getAttribute('UserID')
            if sellerID not in users:
                users.append(sellerID)
                writeUser(item, sellerID) # Write tuple into User table ONLY if haven't already encountered
                
        # Keep track of previously encountered bidders/sellers by storing them in a list to avoid duplicates. Only want each seller posted once.      
        bidderIDlist = item.getElementsByTagName('Bidder')
        for b in bidderIDlist:
            bidderID = b.getAttribute('UserID')
            if bidderID not in users:
                users.append(bidderID)
                writeUser(item, bidderID) # Write tuple into User table ONLY if haven't already encountered

        # Write all tuples into Bid table
        bidslist = item.getElementsByTagName('Bids')
        if len(bidslist) != 0:
            for bids in bidslist:
                bidlist = bids.getElementsByTagName('Bid')
                for b in bidlist:
                    writeBid(item)
                
        #Write tuple into Category
        writeCategory(item)



def main():
    if len(sys.argv) <= 1:
        print("Usage: python3", sys.argv[0], "[file] [file] ...")

    #locale.setlocale(locale.LC_ALL, 'en_US.UTF8')
    for filename in sys.argv[1:]:
        process_file(filename)

if __name__ == "__main__":
    main()
