import React, { useState, useEffect, FormEvent } from 'react';
import { Container, Row, Col, Form } from 'react-bootstrap';
import { Scatter, ChartData } from 'react-chartjs-2';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'App.css';

const SERVER_URL = window.location.port === '3000'
  ? 'http://127.0.0.1:5000'
  : `${window.location.protocol}://${window.location.hostname}:${window.location.port}`;

const LINE_COLORS = [
  '#FF4B00',
  '#FFF100',
  '#03AF7A',
  '#005AFF',
  '#4DC4FF',
  '#FF8082',
  '#F6AA00',
  '#990099',
  '#804000',
];

function App() {
  const [lensList, setLensList] = useState<{ 'id': number, 'name': string, 'device': string }[]>([]);
  const [selectedLensIdList, setSelectedLensIdList] = useState<number[]>([]);
  const [chartData, setChartData] = useState<ChartData<Chart.ChartData>>({ datasets: [] });
  const [dataType, setDataType] = useState('center');
  const [fValue, setFValue] = useState('-1');

  useEffect(() => {
    fetch(`${SERVER_URL}/api/lenses`).then(res => res.json()).then(res => setLensList(res));
  }, []);

  useEffect(() => {
    const init = async () => {
      const temp: ChartData<Chart.ChartData> = { datasets: [] };
      let index = 0;
      for (const lensId of selectedLensIdList) {
        const lensName = lensList.filter(record => record.id == lensId)[0].name;
        const temp2: Chart.ChartDataSets = {
          label: lensName,
          fill: false,
          borderWidth: 2,
          borderColor: LINE_COLORS[index % LINE_COLORS.length],
          pointBorderColor: LINE_COLORS[index % LINE_COLORS.length],
          pointBackgroundColor: LINE_COLORS[index % LINE_COLORS.length],
          showLine: true,
          pointRadius: 3,
          data: []
        };
        const score: { 'focal': number, 'score': number }[] = await (await fetch(`${SERVER_URL}/api/lenses/${lensId}/${dataType}/${fValue}`)).json();
        for (const record of score) {
          (temp2.data as Chart.ChartPoint[]).push({ x: record.focal, y: record.score });
        }
        (temp.datasets as Chart.ChartDataSets[]).push(temp2);
        index += 1;
      }
      setChartData(temp);
    };
    init();
  }, [selectedLensIdList, dataType, fValue]);

  const onSelectLenses = (e: FormEvent<HTMLSelectElement>) => {
    const temp: number[] = [];
    for (let i = 0; i < e.currentTarget.options.length; i += 1) {
      if (e.currentTarget.options[i].selected) {
        temp.push(lensList[i].id);
      }
    }
    setSelectedLensIdList(temp);
  };

  const onChangeDataType = (e: FormEvent<HTMLSelectElement>) => {
    setDataType(e.currentTarget.value);
  }

  const onChangeFValue = (e: FormEvent<HTMLSelectElement>) => {
    setFValue(e.currentTarget.value);
  }

  return (
    <Container>
      <Row>
        <Col sm={6}>
          <Form className="my-3">
            <Form.Group controlId="lensList">
              <Form.Label>レンズを選択</Form.Label>
              <select multiple className="form-control" size={10} onChange={onSelectLenses}>
                {
                  lensList.map(record => {
                    return <option key={record.id}>[{record.device}] {record.name}</option>
                  })
                }
              </select>
            </Form.Group>
            <Form.Group controlId="dataType">
              <Form.Control as="select" value={dataType} onChange={onChangeDataType}>
                <option value="center">中央部</option>
                <option value="edge">周辺</option>
              </Form.Control>
            </Form.Group>
            <Form.Group controlId="dataType">
              <Form.Control as="select" value={fValue} onChange={onChangeFValue}>
                <option value="-1">最高値</option>
                <option value="0">絞り開放</option>
                <option value="2.8">F2.8</option>
                <option value="4">F4</option>
                <option value="5.6">F5.6</option>
                <option value="8">F8</option>
                <option value="11">F11</option>
              </Form.Control>
            </Form.Group>
          </Form>
        </Col>
        <Col>
          <Scatter width={450} height={450} data={chartData}
            options={{
              elements: { line: { tension: 0 } },
              scales: {
                xAxes: [{ scaleLabel: { display: true, labelString: '焦点距離[mm]' }, }],
                yAxes: [{ scaleLabel: { display: true, labelString: 'スコア' }, }]
              },
              showLines: true,
              animation: {duration: 0}
            }} redraw />
        </Col>
      </Row>
    </Container>
  );
}

export default App;
