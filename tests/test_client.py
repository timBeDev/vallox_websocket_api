import mock
from unittest import TestCase
import binascii

from vallox_websocket_api import Client

class TestClient(TestCase):
  @mock.patch('vallox_websocket_api.client.websocket.create_connection', autospec=True)
  def testFetchMetric(self, mock_websocket_create_connection):
    client = Client('127.0.0.1')

    ws = mock.Mock()
    ws.recv.return_value = binascii.unhexlify('0024000000000000000000000000000001000800030000000000000061df98b100030003203fb9500331000000000000000000560000000000000000000000000000000000000000001b00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002b000f732a6ca969a171d1730800010000022700000028000000000000000001a6029e000100000028ffffffffffffffffffffffffffffffffffffffffffffffff000000000000000057c503e8ffffffffffff000000190000000000010000000000000000000300001b98012000a50000000000000000001e00010000000100000000000000000007001b000f001700010012000200070044000000010000000000000007003200320001000000000000001e0000c0a80501ffffff0000000000000000000000000000000000000000000000000000000000c0a8050c86076097f78844b7ac4db61e502fe4f2004c004c000100c00101001c001e000a00320000003703840000708f00320032000a0000000000010000000a721f0000000000010000000f728300000000000000000064715700000000000000000000000000000000000000010037001e000000000000000068bf71bb000083910000002600b4000000010001000000010001001e000f00080001001200000003000000000000000000000017000003e90000000000000001000100010000000a003200010000000000000000000000000000000000000000001000000000000000000000000000540048000000000000000000000000000000c8000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a9000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')
    mock_websocket_create_connection.return_value = ws

    self.assertEqual(1, client.fetch_metric('A_CYC_ENABLED'))

    ws.send.assert_called_once_with(binascii.unhexlify('0300f6000000f900'), opcode=0x2)

  @mock.patch('vallox_websocket_api.client.websocket.create_connection', autospec=True)
  def testSetValue(self, mock_websocket_create_connection):
    client = Client('127.0.0.1')

    ws = mock.Mock()
    ws.recv.return_value = binascii.unhexlify('0200f500f700')
    mock_websocket_create_connection.return_value = ws

    client.set_values({
      'A_CYC_STATE': 0,
      'A_CYC_BOOST_TIMER': 0,
      'A_CYC_FIREPLACE_TIMER': 0,
      'A_CYC_EXTRA_TIMER': 0
    })

    ws.send.assert_called_once_with(binascii.unhexlify('0a00f900011200000412000005120000061200001349'), opcode=0x2)

  @mock.patch('vallox_websocket_api.client.websocket.create_connection', autospec=True)
  def testSetAssertion(self, mock_websocket_create_connection):
    client = Client('127.0.0.1')

    ws = mock.Mock()
    ws.recv.return_value = binascii.unhexlify('0200f500f700')
    mock_websocket_create_connection.return_value = ws

    with self.assertRaises(AssertionError) as context:
      client.set_values({
        'A_CYC_BOOST_TIMER': '11.2'
      })

    with self.assertRaises(ValueError) as context:
      client.set_values({
        'A_CYC_BOOST_AIR_TEMP_TARGET': '11.2'
      })

    with self.assertRaises(AssertionError) as context:
      client.set_values({
        'A_CYC_BOOST_SPEED_SETTING': '11.2'
      })

    with self.assertRaises(AssertionError) as context:
      client.set_values({
        'A_CYC_FIREPLACE_SUPP_FAN': '11.2'
      })

  @mock.patch('vallox_websocket_api.client.websocket.create_connection', autospec=True)
  def testSetMissing(self, mock_websocket_create_connection):
    client = Client('127.0.0.1')

    ws = mock.Mock()
    ws.recv.return_value = binascii.unhexlify('0200f500f700')
    mock_websocket_create_connection.return_value = ws

    with self.assertRaises(AttributeError) as context:
      client.set_values({
        'A_CYC_BOOSTER': 10
      })

  @mock.patch('vallox_websocket_api.client.websocket.create_connection', autospec=True)
  def testSetUnsettable(self, mock_websocket_create_connection):
    client = Client('127.0.0.1')

    ws = mock.Mock()
    ws.recv.return_value = binascii.unhexlify('0200f500f700')
    mock_websocket_create_connection.return_value = ws

    with self.assertRaises(AttributeError) as context:
      client.set_values({
        'A_CYC_RH_VALUE': 22
      })

  @mock.patch('vallox_websocket_api.client.websocket.create_connection', autospec=True)
  def testSetNewSettableAddressByName(self, mock_websocket_create_connection):
    client = Client('127.0.0.1')

    ws = mock.Mock()
    ws.recv.return_value = binascii.unhexlify('0200f500f700')
    mock_websocket_create_connection.return_value = ws

    client.set_settable_address('A_CYC_RH_VALUE', int)

    client.set_values({
      'A_CYC_RH_VALUE': 22
    })

  @mock.patch('vallox_websocket_api.client.websocket.create_connection', autospec=True)
  def testSetNewSettableAddressByAddress(self, mock_websocket_create_connection):
    client = Client('127.0.0.1')

    ws = mock.Mock()
    ws.recv.return_value = binascii.unhexlify('0200f500f700')
    mock_websocket_create_connection.return_value = ws

    client.set_settable_address(4363, int)

    client.set_values({
      'A_CYC_RH_VALUE': 22
    })