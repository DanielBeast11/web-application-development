def calc(depreciation, resource_mileage=500000):
    total_depreciation = 0

    cars = depreciation["cars"]
    for car in cars:
        car_price = car['price']
        mileage = car['mileage']

        if resource_mileage == 0:
            resource_mileage = 1  # Избегаем деления на ноль

        car_depreciation = (car_price * mileage) / resource_mileage

        # Ограничиваем амортизацию начальной стоимостью
        car_depreciation = min(car_depreciation, car_price)

        total_depreciation += car_depreciation * 10

    return round(total_depreciation, 2)