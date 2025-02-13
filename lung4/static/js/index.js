
var canvas = document.getElementById("canvas");

var ctx = canvas.getContext("2d");

canvas.height = window.innerHeight;
canvas.width = window.innerWidth;

// 定义一个粒子数组
var particlesArray = [];
// 定义页面内粒子的数量
var count = parseInt(canvas.width / 80 * canvas.height / 80);

// 定义粒子类
class Particle {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        // x，y轴的移动速度  -0.5 -- 0.5
        this.directionX = Math.random() - 0.5;
        this.directionY = Math.random() - 0.5;
    }

    // 更新点的坐标
    update() {
        this.x += this.directionX;
        this.y += this.directionY;
    }

    // 绘制粒子
    draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, 2, 0, Math.PI * 2);
        ctx.closePath();
        ctx.fillStyle = "white";
        ctx.fill();
    }
}

// 创建粒子
function createParticle() {
    // 生成一个点的随机坐标
    var x = Math.random() * window.innerWidth;
    var y = Math.random() * window.innerHeight;

    particlesArray.push(new Particle(x, y));
}

// 处理粒子
// 先更新坐标，再绘制出来
function handleParticle() {
    for (var i = 0; i < particlesArray.length; i++) {
        var particle = particlesArray[i];
        particle.update();
        particle.draw();
        // 超出范围就将这个粒子删除
        if (particle.x < 0 || particle.x > canvas.width || particle.y < 0 || particle.y > canvas.height) {
            particlesArray.splice(i, 1);
        }

        // 绘制两个点之间的连线
        for (var j = i + 1; j < particlesArray.length; j++) {
            var dx = particlesArray[j].x - particlesArray[i].x;
            var dy = particlesArray[j].y - particlesArray[i].y;
            var dist = Math.sqrt(Math.pow(dx, 2) + Math.pow(dy, 2));
            if (dist < 100) {
                ctx.beginPath();
                ctx.strokeStyle = "rgba(255, 255, 255, " + (1 - dist / 100) + ")";
                ctx.moveTo(particlesArray[i].x, particlesArray[i].y);
                ctx.lineTo(particlesArray[j].x, particlesArray[j].y);
                ctx.closePath();
                ctx.lineWidth = 1;
                ctx.stroke();
            }
        }
    }
}

function draw() {
    // 首先清空画布
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // 如果粒子数量小于规定数量，就生成新的粒子
    if (particlesArray.length < count) {
        createParticle();
    }

    // 处理粒子
    handleParticle();
}

// 设置定时器
setInterval(draw, 10);

// 窗口调整时，重新设置canvas的宽高
window.addEventListener('resize', function () {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
});
