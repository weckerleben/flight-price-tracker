def build_url(airline, go_date, back_date):
    base_urls = {
        'latam': 'https://www.latamairlines.com/py/es/ofertas-vuelos/?origin=ASU&destination=FRA&adt=1&chd=0&inf=0&trip=RT&cabin=Economy&redemption=false&sort=PRICE%2Casc',
        'skyscanner': 'https://www.espanol.skyscanner.com/transporte/vuelos/asu/fra',
        'kayak': 'https://www.kayak.com/flights/ASU-FRA'
    }

    if airline == 'kayak':
        filters = "sort=price_a&fs=cfc=1;price=-1800;legdur=-1500;stops=1;bfc=1"
        return f"{base_urls[airline]}/{go_date}/{back_date}?{filters}"
    else:
        raise ValueError("Airline not supported")
