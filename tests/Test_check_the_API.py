import datetime

import pytest
import requests
from lxml import etree


def get_currency_xml(date=None):
    url = 'http://www.cbr.ru/scripts/XML_daily.asp'
    params = {}
    if date:
        params["date_req"] = date.strftime("%d/%m/%Y")
    response = requests.get(url, params=params)
    return response.content


def get_currency_xsd():
    url = 'http://www.cbr.ru/StaticHtml/File/92172/ValCurs.xsd'
    response = requests.get(url)
    return response.content


@pytest.fixture(scope='module')
def currency_xml():
    xml = get_currency_xml()
    return etree.fromstring(xml)


def test_valid_xml():
    xml = get_currency_xml()
    assert xml

    try:
        currency_xml = etree.fromstring(xml)
    except etree.XMLSyntaxError:
        pytest.fail('Invalid XML')

    assert currency_xml


def test_validate_by_xsd(currency_xml):
    xmlschema_doc = etree.fromstring(get_currency_xsd())
    xmlschema = etree.XMLSchema(xmlschema_doc)

    result = xmlschema.validate(currency_xml)
    assert result


def test_currency_fields_exist(currency_xml):
    expected_fields = ['NumCode', 'CharCode', 'Nominal', 'Name', 'Value']
    for field in expected_fields:
        assert currency_xml.xpath(f'//Valute/{field}')


def test_currency_codes(currency_xml):
    # from https://en.wikipedia.org/wiki/ISO_4217
    currencies = {'AED', 'AFN', 'ALL', 'AMD', 'ANG', 'AOA', 'ARS', 'AUD', 'AWG', 'AZN', 'BAM', 'BBD', 'BDT', 'BGN',
                  'BHD', 'BIF', 'BMD', 'BND', 'BOB', 'BOV', 'BRL', 'BSD', 'BTN', 'BWP', 'BYN', 'BZD', 'CAD', 'CDF',
                  'CHE', 'CHF', 'CHW', 'CLF', 'CLP', 'COP', 'COU', 'CRC', 'CUC', 'CUP', 'CVE', 'CZK', 'DJF', 'DKK',
                  'DOP', 'DZD', 'EGP', 'ERN', 'ETB', 'EUR', 'FJD', 'FKP', 'GBP', 'GEL', 'GHS', 'GIP', 'GMD', 'GNF',
                  'GTQ', 'GYD', 'HKD', 'HNL', 'HTG', 'HUF', 'IDR', 'ILS', 'INR', 'IQD', 'IRR', 'ISK', 'JMD', 'JOD',
                  'JPY', 'KES', 'KGS', 'KHR', 'KMF', 'KPW', 'KRW', 'KWD', 'KYD', 'KZT', 'LAK', 'LBP', 'LKR', 'LRD',
                  'LSL', 'LYD', 'MAD', 'MDL', 'MGA', 'MKD', 'MMK', 'MNT', 'MOP', 'MRU', 'MUR', 'MVR', 'MWK', 'MXN',
                  'MXV', 'MYR', 'MZN', 'NAD', 'NGN', 'NIO', 'NOK', 'NPR', 'NZD', 'OMR', 'PAB', 'PEN', 'PGK', 'PHP',
                  'PKR', 'PLN', 'PYG', 'QAR', 'RON', 'RSD', 'CNY', 'RUB', 'RWF', 'SAR', 'SBD', 'SCR', 'SDG', 'SEK',
                  'SGD', 'SHP', 'SLE', 'SLL', 'SOS', 'SRD', 'SSP', 'STN', 'SVC', 'SYP', 'SZL', 'THB', 'TJS', 'TMT',
                  'TND', 'TOP', 'TRY', 'TTD', 'TWD', 'TZS', 'UAH', 'UGX', 'USD', 'USN', 'UYI', 'UYU', 'UYW', 'UZS',
                  'VED', 'VES', 'VND', 'VUV', 'WST', 'XAF', 'XAG', 'XAU', 'XBA', 'XBB', 'XBC', 'XBD', 'XCD', 'XDR',
                  'XOF', 'XPD', 'XPF', 'XPT', 'XSU', 'XTS', 'XUA', 'XXX', 'YER', 'ZAR', 'ZMW', 'ZWL'}

    codes = currency_xml.xpath('//Valute/CharCode/text()')
    for code in codes:
        assert code in currencies


def test_unique_currency_codes(currency_xml):
    codes = currency_xml.xpath('//Valute/CharCode/text()')
    assert len(codes) == len(set(codes))


def test_value_positive(currency_xml):
    values = currency_xml.xpath('//Valute/Value/text()')
    for value in values:
        assert float(value.replace(',', '.')) > 0


def test_validate_num_code(currency_xml):
    num_codes = currency_xml.xpath('//Valute/NumCode/text()')
    for num_code in num_codes:
        assert num_code.isdigit()


def test_validate_nominal(currency_xml):
    nominals = currency_xml.xpath('//Valute/Nominal/text()')
    for nominal in nominals:
        assert nominal.isdigit()


def test_validate_name(currency_xml):
    names = currency_xml.xpath('//Valute/Name/text()')
    for name in names:
        assert name.strip() != ''


def test_with_date():
    xml = get_currency_xml(datetime.date(2023, 6, 24))
    currency_xml = etree.fromstring(xml)

    date = currency_xml.xpath('//ValCurs/@Date')[0]
    assert date == '24.06.2023'
