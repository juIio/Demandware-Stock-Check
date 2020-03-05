import cloudscraper
import atexit
import json
import time

product_sku = 'FX9846'
site = 'yeezysupply'  # Any demandware site (i.e. yeezysupply or adidas)
target_site = 'https://www.' + str(site).lower() + '.com/api/products/' + str(product_sku).upper() + '/availability'
timeout_retry_seconds = 180
refresh_rate_seconds = 15
total_stock = {}
loaded_sizes = {}


def start_scan():
    atexit.register(save_data)

    scraper = cloudscraper.create_scraper()
    live = False

    while True:
        text = scraper.get(target_site).text

        if 'security issue' in text:
            print('\n')
            print('=====================================')
            print('Session has been forbidden on this ip')
            print('=====================================')
            print('\n')

        elif '<title>' in text:
            print('\n')
            print('=============================')
            print('Session has been rate limited')
            print('=============================')
            print('\n')
            print(text)

            time.sleep(timeout_retry_seconds)
        else:
            json_message = json.loads(text)

            if 'message' in json_message:
                # Once the release is done save data and exit
                if live:
                    live = False
                    save_data()

                print('\n')
                print('The product for SKU ' + product_sku + ' was not found.')
                print('\n')

            elif 'id' in json_message:
                sku = json_message['id']
                status = json_message['availability_status']

                print(' ')
                print('SKU: ' + sku)
                print('Availability: ' + status)

                if status == 'IN_STOCK':
                    live = True
                    sizes_in_stock = ''

                    for variation in json_message['variation_list']:
                        size = str(variation['size'])
                        stock_amount_int = variation['availability']
                        stock_amount_string = str(stock_amount_int)

                        if stock_amount_int > 0:
                            sizes_in_stock += size + ', '

                        if size not in loaded_sizes:
                            print(' ')
                            print('   Size: ' + size)
                            print('   Available: ' + stock_amount_string)
                            print('   Status: ' + variation['availability_status'])

                            loaded_sizes[size] = stock_amount_int
                            total_stock[size] = stock_amount_int
                        else:
                            previous_stock = loaded_sizes[size]

                            if previous_stock != stock_amount_int:
                                if stock_amount_int > previous_stock:
                                    total_stock[size] = total_stock[size] + (stock_amount_int - previous_stock)

                                print('=====================================================')
                                print('Stock change for size ' + size)
                                print('New stock: ' + stock_amount_string)
                                print('=====================================================')

                                loaded_sizes[size] = stock_amount_int
                    if sizes_in_stock != '':
                        print('Available sizes: ' + sizes_in_stock[:-2])

        time.sleep(refresh_rate_seconds)


def save_data():
    if len(total_stock) > 0:
        with open('total_stock.json', 'w') as total_stock_file:
            json.dump(total_stock, total_stock_file, sort_keys=True, indent=4)

        print('Saved the total stock to total_stock.json file')
    else:
        print('No stock was loaded, no data saved')


if __name__ == '__main__':
    start_scan()
