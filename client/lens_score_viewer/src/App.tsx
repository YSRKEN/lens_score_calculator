import React, { useState, useEffect, FormEvent } from 'react';
import { Container, Row, Col, Form } from 'react-bootstrap';
import { Scatter, ChartData } from 'react-chartjs-2';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'App.css';
import Chart from 'chart.js';

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
  const [inputedLensId, setInputedLensId] = useState(0);

  useEffect(() => {
    fetch(`${SERVER_URL}/api/lenses`).then(res => res.json()).then(res => setLensList(res));
  }, []);

  useEffect(() => {
    const init = async () => {
      const temp: ChartData<Chart.ChartData> = { datasets: [] };
      let index = 0;
      const scoreHash: {[key: number]: { 'focal': number, 'score': number }[]} = {};
      let maxFocal = 0;
      for (const lensId of selectedLensIdList) {
        const temp: { 'focal': number, 'score': number }[] = await (await fetch(`${SERVER_URL}/api/lenses/${lensId}/${dataType}/${fValue}`)).json();
        scoreHash[lensId] = temp;
        maxFocal = Math.max(...[maxFocal, ...temp.map(r => r.focal)]);
      }
      for (const lensId of selectedLensIdList) {
        const lensName = lensList.filter(record => record.id === lensId)[0].name;
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
        const score: { 'focal': number, 'score': number }[] = scoreHash[lensId];
        for (const record of score) {
          (temp2.data as Chart.ChartPoint[]).push({ x: record.focal, y: record.score });
        }
        (temp.datasets as Chart.ChartDataSets[]).push(temp2);

        const maxFocal2 = Math.max(...scoreHash[lensId].map(r => r.focal));
        if (scoreHash[lensId].filter(r => r.focal === maxFocal2).length > 0) {
          const color = Chart.helpers.color(LINE_COLORS[index % LINE_COLORS.length]).alpha(0.5).rgbString();
          const temp3: Chart.ChartDataSets = {
            label: '',
            fill: false,
            borderWidth: 2,
            borderColor: color,
            showLine: true,
            pointRadius: 0,
            data: []
          };
          const maxFocalScore = scoreHash[lensId].filter(r => r.focal === maxFocal2)[0].score;
          for (let i = maxFocal2; i <= maxFocal; i += 1) {
            (temp3.data as Chart.ChartPoint[]).push({ x: i, y: 1.0 * maxFocalScore * maxFocal2 / i });
          }
          (temp.datasets as Chart.ChartDataSets[]).push(temp3);
        }
        index += 1;
      }
      setChartData(temp);
    };
    init();
  }, [selectedLensIdList, dataType, fValue, lensList]);

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

  const onChangeInputedLensId = (e: FormEvent<HTMLInputElement>) => {
    const temp = parseInt(e.currentTarget.value, 10);
    if (!isNaN(temp)) {
      setInputedLensId(Math.abs(Math.round(temp)));
    } else {
      setInputedLensId(0);
    }
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
          <div className="my-3">
            <Scatter width={450} height={450} data={chartData}
              options={{
                elements: { line: { tension: 0 } },
                scales: {
                  xAxes: [{ scaleLabel: { display: true, labelString: '焦点距離[mm]' }, }],
                  yAxes: [{ scaleLabel: { display: true, labelString: 'スコア[LW/PH]' }, }]
                },
                showLines: true,
                animation: { duration: 0 }
              }} redraw />
          </div>
        </Col>
      </Row>
      <hr style={{borderWidth: 5}}/>
      <Row>
        <Col sm={6}>
        <Form className="my-3">
            <Form.Group controlId="lensList">
              <Form.Label>レンズID</Form.Label>
              <Form.Control value={`${inputedLensId}`} onChange={onChangeInputedLensId}/>
            </Form.Group>
          </Form>
        </Col>
      </Row>
    </Container>
  );
}

export default App;
