import scrapy 
import requests
import os
import json


# Creating Directory and URL of each category
class pepperfrySpider(scrapy.Spider):
    name = "pepperfry"
    MAX_CNT = 20    # Scrap max 20 products
    base_dir = "C:\\Users\\user\\Desktop\\Python\\Vscode\\PepperFry\\pepperfry_data"
    
    def start_requests(self):

        parent_dir = "C:\\Users\\user\\Desktop\\Python\\Vscode\\PepperFry\\pepperfry_data"
        urls = []
        dir_names=[ ]
        category = []
        # Coding Blocks Categories :-
        #'arm chair','bean bag','bench','book case','chest drawers','coffee tables','dining set',
        #'garden seating','king beds','queen beds','two seater sofa'

        print("-----------------------------------------------------------------------------")
        n = int(input("Enter number of categories you want : "))
        print("Enter category names : ")
        for i in range(n):
            ctg = input()
            category.append(ctg) 
        print("-----------------------------------------------------------------------------")

        for i in category:
            url_query = i.replace(" ","+")
            url = f"https://www.pepperfry.com/site_product/search?q={url_query}"
            dir_name = i.replace(" ","-")
            dir_names.append(dir_name)
            path = os.path.join(parent_dir, dir_name)
            os.makedirs(path)
            urls.append(url)
            
        # making response
        for i in range(len(urls)):
            resp = scrapy.Request(url=urls[i],callback=self.parse,dont_filter=True)
            resp.meta['dir_name'] = dir_names[i]
            yield resp

    def parse(self, response, **meta):
        #product_urls = response.xpath('//div/div/div/a[@p=0]/@href').extract()
        product_urls = response.css("a.clip-prd-dtl::attr(href)").getall()
        counter = 0
        for url in product_urls:
            resp = scrapy.Request(url=url, callback=self.parse_item,dont_filter=True)
            resp.meta['dir_name'] = response.meta['dir_name']
            
            if counter == self.MAX_CNT:   # Scrap max 20 products
                break
            if not resp == None:          
                counter+=1
            yield resp

    def parse_item(self, response,**meta):

        # Getting Product Info from link2product
        metadata= {}

        all_product_images = response.css("div.vipImage__thumb-wrapper a::attr(data-img)").getall()
        name = response.css("h1.v-pro-ttl::text").get()
        price = response.css("span.v-offer-price-amt::text").get()
        MRP = response.css("span.v-price-mrp-amt::attr(data-price)").get()
        savings = response.css("span.v-price-save-ttl-amt::text").get()[2:-2]
        desc = response.css("div.v-more-info-tab-cont-para-wrap p::text").get()

        metadata['Product Name'] = name
        metadata['Price'] = f"Rs. {price}"
        metadata['MRP'] = f"Rs. {MRP}"
        metadata['Savings'] = f"Rs. {savings}"
        metadata['description'] = desc

        # To get Product Details
        for i in response.css(("div.v-prod-comp-dtls-listitem")): 
            title = i.css("span.v-prod-comp-dtls-listitem-label::text").get()
            value  = i.css("span.v-prod-comp-dtls-listitem-value::text").get()
            metadata[f'{title}'] = value
            
        del metadata['None']

        category_name = response.meta['dir_name']  

        #os.path.join(self.base_dir, os.path.join(category_name, name))
        item_dir_url = f"C:\\Users\\user\\Desktop\\Python\\Vscode\\PepperFry\\pepperfry_data\\{category_name}\\{name}"
        if not os.path.exists(item_dir_url):
            os.makedirs(item_dir_url)
            
        # Save metadata
        with open(os.path.join(item_dir_url,'metadata.txt'),'w') as f:
            json.dump(metadata,f)
            
        #Saving images
        for i,img_url in enumerate(all_product_images):
            r= requests.get(img_url)
            with open(os.path.join(item_dir_url,f"image{i}.jpg"),'wb') as f:
                f.write(r.content)

        yield None