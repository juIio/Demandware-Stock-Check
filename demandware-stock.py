import cloudscraper
import json
import time

product_sku = 'FV4440'
site = 'yeezysupply'  # Any demandware site (i.e. yeezysupply or adidas)
target_site = 'https://www.' + str(site).lower() + '.com/api/products/' + str(product_sku).upper() + '/availability'
timeout_retry_seconds = 180
refresh_rate_seconds = 5
total_stock = {}
loaded_sizes = {}


def start_scan():
    scraper = cloudscraper.create_scraper()
    live = False

    while True:
        text = scraper.get(target_site).text

        if "<title>" in text:
            print('\n')
            print('=============================')
            print('Session has been rate limited')
            print('=============================')
            print('\n')

            time.sleep(timeout_retry_seconds)
        else:
            json_message = json.loads(text)

            if 'message' in json_message:
                print('\n')
                print('The product for SKU ' + product_sku + ' was not found.')
                print('\n')

            elif 'id' in json_message:
                sku = json_message['id']
                status = json_message['availability_status']

                print('\n')
                print('SKU: ' + sku)
                print('Availability: ' + status)

                # Once it's back into preview from being live save total stock
                if status == 'PREVIEW' and live:
                    live = False

                    with open('total_stock.json', 'w') as file:
                        json.dump(total_stock, file, sort_keys=True, indent=4)

                    print('Saved the total stock to total_stock.json file')
                    exit(1)

                elif status == 'IN_STOCK':
                    for variation in json_message['variation_list']:
                        size = str(variation['size'])
                        stock_amount_string = str(variation['availability'])

                        if size not in loaded_sizes:
                            print('   Size: ' + size)
                            print('   Available: ' + stock_amount_string)
                            print('   Status: ' + variation['availability_status'])

                            loaded_sizes[size] = int(stock_amount_string)
                            total_stock[size] = int(stock_amount_string)
                        else:
                            previous_stock = loaded_sizes[size]
                            current_stock = int(stock_amount_string)

                            if previous_stock != current_stock:
                                if current_stock > previous_stock:
                                    total_stock[size] = total_stock[size] + (current_stock - previous_stock)

                                print('=====================================================')
                                print('Stock change for size ' + size)
                                print('New stock: ' + stock_amount_string)
                                print('=====================================================')
                print('\n')

        time.sleep(refresh_rate_seconds)


if __name__ == '__main__':
    start_scan()
