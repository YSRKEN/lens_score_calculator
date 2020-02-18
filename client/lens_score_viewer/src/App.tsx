import React, { useState, useEffect, FormEvent } from 'react';
import { Container, Row, Col, Form } from 'react-bootstrap';
import { Scatter } from 'react-chartjs-2';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'App.css';

const SERVER_URL = window.location.port === '3000'
  ? 'http://127.0.0.1:5000'
  : `${window.location.protocol}://${window.location.hostname}:${window.location.port}`;

function App() {
  const [lensList, setLensList] = useState<{'id': number, 'name': string, 'device': string}[]>([]);
  const [selectedLensIdList, setSelectedLensIdList] = useState<number[]>([]);
  
  useEffect(() => {
    fetch(`${SERVER_URL}/api/lenses`).then(res => res.json()).then(res => setLensList(res));
  }, []);

  useEffect(()=>{
    console.log(selectedLensIdList);
  }, [selectedLensIdList]);

  const onSelectLenses = (e: FormEvent<HTMLSelectElement>) => {
    const temp: number[] = [];
    for (let i = 0; i < e.currentTarget.options.length; i += 1) {
      if (e.currentTarget.options[i].selected) {
        temp.push(lensList[i].id);
      }
    }
    setSelectedLensIdList(temp);
  };

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
                    return <option key={record.id}>{record.name}</option>
                  })
                }
              </select>
            </Form.Group>
          </Form>
        </Col>
        <Col>
          <Scatter width={450} height={450} data={{
            datasets: [{
              label: 'sample-1',
              fill: false,
              borderWidth: 2,
              borderColor: '#FF0000',
              pointBorderColor: '#FF0000',
              pointBackgroundColor: '#FF0000',
              showLine: true,
              pointRadius: 3,
              data: [
                { x: 14, y: 3000 },
                { x: 28, y: 2500 },
                { x: 56, y: 2000 },
                { x: 72, y: 1500 },
              ]
            }]
          }}
            options={{
              elements: { line: { tension: 0 } },
              scales: {
                xAxes: [{ scaleLabel: { display: true, labelString: '焦点距離[mm]' }, }],
                yAxes: [{ scaleLabel: { display: true, labelString: 'スコア' }, }]
              },
              showLines: true
            }} />
        </Col>
      </Row>
    </Container>
  );
}

export default App;
