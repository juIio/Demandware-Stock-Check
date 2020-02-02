import cloudscraper
import json
import time

product_sku = 'FX9034'
site = 'yeezysupply'  # Any demandware site (i.e. yeezysupply or adidas)
target_site = 'https://www.' + site + '.com/api/products/' + product_sku + '/availability'
timeout_retry_seconds = 180
refresh_rate_seconds = 5
stored_sizes = {}


def start_scan():
    scraper = cloudscraper.create_scraper()

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
                print('\n')
                print('SKU: ' + json_message['id'])
                print('Availability: ' + json_message['availability_status'])

                for variation in json_message['variation_list']:
                    size = str(variation['size'])
                    stock_amount = str(variation['availability'])

                    if size not in stored_sizes:
                        print('   Size: ' + size)
                        print('   Available: ' + stock_amount)
                        print('   Status: ' + variation['availability_status'])

                        stored_sizes[size] = stock_amount
                    else:
                        previous_stock = stored_sizes[size]

                        if previous_stock != stock_amount:
                            print('=====================================================')
                            print('Stock change for size ' + size)
                            print('New stock: ' + stock_amount)
                            print('=====================================================')
                print('\n')

        time.sleep(refresh_rate_seconds)


if __name__ == '__main__':
    start_scan()
