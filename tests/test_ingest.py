from pipeline.ingest import IngestionConfig, run_ingest
from pipeline.models import StepResult
from pipeline import WORKING_DIR


def test_ingest_offline_sample(tmp_path, monkeypatch):
    output = tmp_path / 'ingested.csv'
    config = IngestionConfig(limit=9, countries=("PT", "ANG", "CV"), prefer_online=False)
    result = run_ingest(config, output=output)
    assert isinstance(result, StepResult)
    assert result.status == 'ok'
    assert result.metrics['total_records'] >= 6
    data = output.read_text(encoding='utf-8').splitlines()
    header = data[0].split(',')
    assert 'provenance' in header
    assert 'source_type' in header
