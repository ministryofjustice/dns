from unittest.mock import MagicMock, patch

import pytest
from check_empty_zones import get_aws_zones, is_zone_empty, main


@pytest.fixture
def mock_boto3_client():
    with patch('boto3.client') as mock_client:
        yield mock_client


def test_get_aws_zones(mock_boto3_client):
    mock_paginator = MagicMock()
    mock_paginator.paginate.return_value = [
        {
            'HostedZones': [
                {'Id': '/hostedzone/Z1234567890ABC', 'Name': 'example.com.'},
                {'Id': '/hostedzone/Z0987654321DEF', 'Name': 'test.com.'}
            ]
        }
    ]
    mock_boto3_client.return_value.get_paginator.return_value = mock_paginator

    result = get_aws_zones()
    assert result == [
        ('/hostedzone/Z1234567890ABC', 'example.com.'),
        ('/hostedzone/Z0987654321DEF', 'test.com.')
    ]


def test_is_zone_empty_true(mock_boto3_client):
    mock_paginator = MagicMock()
    mock_paginator.paginate.return_value = [
        {
            'ResourceRecordSets': [
                {'Type': 'NS'},
                {'Type': 'SOA'}
            ]
        }
    ]
    mock_boto3_client.return_value.get_paginator.return_value = mock_paginator

    assert is_zone_empty('dummy_zone_id') == True


def test_is_zone_empty_false(mock_boto3_client):
    mock_paginator = MagicMock()
    mock_paginator.paginate.return_value = [
        {
            'ResourceRecordSets': [
                {'Type': 'NS'},
                {'Type': 'SOA'},
                {'Type': 'A'}
            ]
        }
    ]
    mock_boto3_client.return_value.get_paginator.return_value = mock_paginator

    assert is_zone_empty('dummy_zone_id') == False


@patch('check_empty_zones.get_aws_zones')
@patch('check_empty_zones.is_zone_empty')
def test_main_empty_zones(mock_is_zone_empty, mock_get_aws_zones, capsys):
    mock_get_aws_zones.return_value = [
        ('/hostedzone/Z1234567890ABC', 'example.com.'),
        ('/hostedzone/Z0987654321DEF', 'test.com.')
    ]
    mock_is_zone_empty.side_effect = [True, False]

    with pytest.raises(SystemExit) as e:
        main()

    assert e.value.code == 1
    captured = capsys.readouterr()
    assert "The following hosted zones are empty:" in captured.out
    assert "  - example.com" in captured.out
    assert "  - test.com" not in captured.out


@patch('check_empty_zones.get_aws_zones')
@patch('check_empty_zones.is_zone_empty')
def test_main_no_empty_zones(mock_is_zone_empty, mock_get_aws_zones, capsys):
    mock_get_aws_zones.return_value = [
        ('/hostedzone/Z1234567890ABC', 'example.com.'),
        ('/hostedzone/Z0987654321DEF', 'test.com.')
    ]
    mock_is_zone_empty.return_value = False

    with pytest.raises(SystemExit) as e:
        main()

    assert e.value.code == 0
    captured = capsys.readouterr()
    assert "No empty hosted zones found." in captured.out
