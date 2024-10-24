let pos = null;
let angle = -90;
let vel = null;

// const walls = [];

function fetchDirection() {
  return new Promise((resolve, reject) => {
    fetch("http://localhost:8080/")
      .then((res) => res.json())
      .then(({ data }) => {
        const { dir } = data;
        const dirVec = createVector(dir.x, dir.y);
        resolve(dirVec);
      })
      .catch(reject);
  });
}

function setup() {
  createCanvas(innerWidth - 1, innerHeight - 5);
  rectMode(CENTER);
  angleMode(DEGREES);
  frameRate(60);
  pos = createVector(width / 2, height / 2);
  vel = createVector(0, 0);
}

function draw() {
  background(50);
  translate(pos.x, pos.y);
  rotate(angle);

  stroke("255");
  strokeWeight(2);
  fill(0, 0);
  arc(0, 0, 56, 56, -45, 45);

  stroke(200);
  strokeWeight(1);
  fill(0);
  ellipse(0, 0, 40, 40);

  if (frameCount % 3 === 0) {
    fetchDirection()
      .then((dir) => {
        angle += dir.x;
        vel.y = dir.y;
      })
      .catch(console.error);
  }
  if (pos.x > width || pos.x < 0 || pos.y > height || pos.y < 0) {
    pos.x = width / 2;
    pos.y = height / 2;
  }

  const dir = p5.Vector.fromAngle(radians(angle));
  pos.add(dir.mult(vel.y));
}
