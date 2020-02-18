import React, { useEffect } from 'react';
import { Container, Row, Col, Form, FormControl } from 'react-bootstrap';
import { Scatter } from 'react-chartjs-2';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'App.css';

function App() {
  return (
    <Container>
      <Row>
        <Col sm={3}>
          <Form className="my-3">
            <Form.Group controlId="lensList">
              <Form.Label>レンズを選択</Form.Label>
              <select multiple className="form-control" size={10}>
                <option>sample-1</option>
                <option>sample-2</option>
                <option>sample-3</option>
                <option>sample-4</option>
                <option>sample-5</option>
                <option>sample-6</option>
                <option>sample-7</option>
                <option>sample-8</option>
                <option>sample-9</option>
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
