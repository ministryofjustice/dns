from unittest.mock import mock_open, patch

import pytest
from check_unmanaged_zones import get_aws_zones, get_config_zones, main

mock_aws_zones = ["example.com", "test.com", "unmanaged.com"]

mock_config_files = ["example.com.yaml", "test.com.yaml"]


def test_get_aws_zones():
    with patch("boto3.client") as mock_boto3:
        mock_paginator = mock_boto3.return_value.get_paginator.return_value
        mock_paginator.paginate.return_value = [
            {"HostedZones": [{"Name": f"{zone}."} for zone in mock_aws_zones]}
        ]

        result = get_aws_zones()
        assert result == set(mock_aws_zones)


def test_get_config_zones():
    with patch("os.listdir", return_value=mock_config_files):
        result = get_config_zones()
        expected = set(["example.com", "test.com"])
        assert result == expected


@pytest.mark.parametrize(
    "aws_zones,config_zones,expected_exit_code,expected_output",
    [
        (
            ["example.com", "test.com"],
            ["example.com", "test.com"],
            0,
            "All AWS Route53 zones are managed by octoDNS.",
        ),
        (
            ["example.com", "test.com", "unmanaged.com"],
            ["example.com", "test.com"],
            1,
            "The following zones exist in AWS but are not managed by octoDNS:\n  - unmanaged.com",
        ),
    ],
)
def test_main(aws_zones, config_zones, expected_exit_code, expected_output, capsys):
    with patch(
        "check_unmanaged_zones.get_aws_zones", return_value=set(aws_zones)
    ), patch(
        "check_unmanaged_zones.get_config_zones", return_value=set(config_zones)
    ), pytest.raises(
        SystemExit
    ) as exit_info:
        main()

    assert exit_info.value.code == expected_exit_code
    captured = capsys.readouterr()
    assert captured.out.strip() == expected_output
