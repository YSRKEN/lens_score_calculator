import React, { useState, useEffect, FormEvent } from 'react';
import { Container, Row, Col, Form, Button, Table } from 'react-bootstrap';
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

interface BasePreData {
  result: string;
}

interface ImagePreData extends BasePreData {
  type: string;
  title: string;
  data: string;
}

interface TextPreData extends BasePreData {
  type: string;
  title: string;
  data: {
    center: number,
    edge: number,
    f: string,
    focal: string
  }[];
}

const LensForm: React.FC<{
  inputedLensId: number,
  lensPreData: BasePreData | ImagePreData | TextPreData,
  refreshLensList: () => void
}> = ({ inputedLensId, lensPreData, refreshLensList }) => {
  const [device, setDevice] = useState('16mp');
  const [recordList, setRecordList] = useState<{ focal: number, f: number, center: number, edge: number }[]>([]);

  useEffect(() => {
    setRecordList([]);
  }, [inputedLensId]);

  const sendLensDataText = () => {
    fetch(`${SERVER_URL}/api/lenses/${inputedLensId}`, {
      method: 'POST',
      mode: "cors",
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ 'device': device })
    }).then(() => refreshLensList());
  };

  const sendLensDataImage = () => {
    fetch(`${SERVER_URL}/api/lenses/${inputedLensId}`, {
      method: 'POST',
      mode: "cors",
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ 'device': device, 'data': recordList })
    }).then(() => refreshLensList());
  };

  const addRecord = () => {
    setRecordList([...recordList, { focal: 0, f: 0, center: 0, edge: 0 }]);
  };

  const editRecord = (index: number, type: string, value: number) => {
    const temp: { focal: number, f: number, center: number, edge: number }[] = [];
    for (let i = 0; i < recordList.length; i += 1) {
      if (index === i) {
        const temp2: {[key: string]: any} = {...recordList[i]};
        temp2[type] = value;
        temp.push(temp2 as { focal: number, f: number, center: number, edge: number });
      } else {
        temp.push({...recordList[i]});
      }
    }
    setRecordList(temp);
  };

  if (lensPreData.result === 'ng') {
    return <Form.Label>エラー：当該レンズデータが存在しません</Form.Label>;
  }
  const temp = lensPreData as (ImagePreData | TextPreData);
  if (temp.type === 'text') {
    return (<>
      <Form.Group>
        <Form.Label>レンズデータを取得しました。</Form.Label><br />
        <Form.Label>レンズ名：{temp.title}</Form.Label><br />
        <Form.Control as="select" value={device} onChange={(e: any) => setDevice(e.currentTarget.value)}>
          <option value="16mp">16mp</option>
          <option value="12mp">12mp</option>
        </Form.Control>
      </Form.Group>
      <Button onClick={sendLensDataText}>送信</Button>
    </>);
  } else {
    const temp2 = temp as ImagePreData;
    return (<>
      <Form.Group>
        <Form.Label>レンズデータを取得しました。</Form.Label><br />
        <Form.Label>レンズ名：{temp2.title}</Form.Label><br />
        <Form.Control as="select" value={device} onChange={(e: any) => setDevice(e.currentTarget.value)}>
          <option value="16mp">16mp</option>
          <option value="12mp">12mp</option>
        </Form.Control>
        <Row className="mt-3">
          <Col>
            <Table striped bordered hover>
              <thead>
                <tr>
                  <th>#</th>
                  <th>焦点距離</th>
                  <th>F値</th>
                  <th>中央部</th>
                  <th>周辺部</th>
                </tr>
              </thead>
              <tbody>
                {
                  recordList.map((record, index) => {
                    return <tr key={index}>
                      <td>{index+1}</td>
                      <td><Form.Control value={'' + record.focal}
                        onChange={(e: any) => editRecord(index, 'focal', parseFloat(e.currentTarget.value))}/></td>
                      <td><Form.Control value={'' + record.f}
                        onChange={(e: any) => editRecord(index, 'f', parseFloat(e.currentTarget.value))}/></td>
                      <td><Form.Control value={'' + record.center}
                        onChange={(e: any) => editRecord(index, 'center', parseFloat(e.currentTarget.value))}/></td>
                      <td><Form.Control value={'' + record.edge}
                        onChange={(e: any) => editRecord(index, 'edge', parseFloat(e.currentTarget.value))}/></td>
                    </tr>;
                  })
                }
              </tbody>
            </Table>
            <Button onClick={addRecord} variant="secondary">項目を追加</Button>
          </Col>
          <Col><img src={temp2.data} /></Col>
        </Row>
      </Form.Group>
      <Button onClick={sendLensDataImage}>送信</Button>
    </>);
  }
  return <></>;
};

function App() {
  const [lensList, setLensList] = useState<{ 'id': number, 'name': string, 'device': string }[]>([]);
  const [selectedLensIdList, setSelectedLensIdList] = useState<number[]>([]);
  const [chartData, setChartData] = useState<ChartData<Chart.ChartData>>({ datasets: [] });
  const [dataType, setDataType] = useState('center');
  const [fValue, setFValue] = useState('-1');
  const [inputedLensId, setInputedLensId] = useState(0);
  const [lensPreData, setLensPreData] = useState<BasePreData | ImagePreData | TextPreData>({ result: 'ng' });

  useEffect(() => {
    refreshLensList();
  }, []);

  useEffect(() => {
    fetch(`${SERVER_URL}/api/lenses/${inputedLensId}/pre`).then(res => res.json()).then(res => setLensPreData(res));
  }, [inputedLensId]);

  useEffect(() => {
    const init = async () => {
      const temp: ChartData<Chart.ChartData> = { datasets: [] };
      let index = 0;
      const scoreHash: { [key: number]: { 'focal': number, 'score': number }[] } = {};
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

  const refreshLensList = () => {
    fetch(`${SERVER_URL}/api/lenses`).then(res => res.json()).then(res => {setLensList(res); setInputedLensId(0);});
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
      <hr style={{ borderWidth: 5 }} />
      <Row>
        <Col>
          <Form className="my-3">
            <Form.Group controlId="lensList">
              <Form.Label>レンズID</Form.Label>
              <Form.Control value={`${inputedLensId}`} onChange={onChangeInputedLensId} />
            </Form.Group>
            <LensForm inputedLensId={inputedLensId} lensPreData={lensPreData} refreshLensList={refreshLensList} />
          </Form>
        </Col>
      </Row>
    </Container>
  );
}

export default App;
