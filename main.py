import pandas as pd
import time
from selenium import webdriver
from functions import preprocess_text, get_product_data
from chromedriver_py import binary_path
import sys
from alive_progress import alive_bar

if __name__ == '__main__':

    #input file
    file_path = sys.argv[1]
    try:
        #SKUs must be in first column with a column name(sku?)!
        input_df = pd.read_excel(file_path, engine = 'pyxlsb')
    except:
        try:
            input_df = pd.read_excel(file_path)

        except Exception as e:
            sys.exit(str(e))

    #Webdriver config to supress the error messages/logs
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options, executable_path=binary_path)

    url = 'https://sodimac.falabella.com/sodimac-cl'
    driver.get(url)
    time.sleep(3)

    #start scrapping
    skus_to_search = input_df[input_df.columns[0]].tolist()
    start = time.time()

    print('\nStarting...')
    data = []
    with alive_bar(len(input_df), force_tty=True) as bar:
        for index, sku in enumerate(skus_to_search, start=1):
            time.sleep(0.005)
            print(f'\n\nextracting sku: {sku}')
            try:
                product_data = get_product_data(driver, sku)
                data.append(product_data)
                bar()

            except Exception as e:
                sys.exit(str(e))

    #save data
    df = pd.DataFrame(data)
    df  = df[['sku', 'cod. tienda', 'descripcion', 'precio', 'precio_dcto','tienda', 'stock_en_tienda', 'url', 'snapshot']]
    date = time.strftime("%D", time.localtime())
    date = date.replace('/','_')
    df.to_csv(f'sodimac_scrapping_{date}.csv')

    #stats
    total_time = time.time() - start
    total_time_min = round(total_time/60, 2)
    avg_time = round(total_time/len(input_df), 0)
    print('\n------------------------------------')
    print(f'Total time taken: {total_time_min} mins')
    print(f'Average time per product: {avg_time} secs')
    print(f'Products Scrapped: {len(input_df)} products')
    print('------------------------------------')
    print(f'file saved as: sodimac_scrapping_{date}.csv')
