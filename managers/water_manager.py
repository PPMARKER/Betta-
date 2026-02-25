import taichi as ti
import numpy as np

# Initialize Taichi
ti.init()

@ti.data_oriented
class WaterManager:
    def __init__(self, num_particles=1500):
        self.num_particles = num_particles
        self.x = ti.Vector.field(2, dtype=ti.f32, shape=num_particles)
        self.v = ti.Vector.field(2, dtype=ti.f32, shape=num_particles)
        self.rho = ti.field(dtype=ti.f32, shape=num_particles)
        self.p = ti.field(dtype=ti.f32, shape=num_particles)

        # Boundaries (Matches Tank Scene)
        self.bound_x = ti.Vector([160.0, 1280.0])
        self.bound_y = ti.Vector([130.0, 640.0])

        # SPH Params
        self.h = 30.0
        self.mass = 1.0
        self.rho0 = 0.2
        self.stiffness = 200.0
        self.viscosity = 0.8
        self.dt = 0.2
        self.gravity = ti.Vector([0.0, 0.4])

        # Grid for acceleration
        self.grid_size = self.h
        self.grid_res_x = int(1440 / self.grid_size) + 1
        self.grid_res_y = int(900 / self.grid_size) + 1
        self.grid_num_particles = ti.field(dtype=ti.i32, shape=(self.grid_res_x, self.grid_res_y))
        self.grid2particles = ti.field(dtype=ti.i32, shape=(self.grid_res_x, self.grid_res_y, 60))

        self.reset()

    @ti.kernel
    def reset(self):
        for i in range(self.num_particles):
            self.x[i] = [ti.random() * (self.bound_x[1] - self.bound_x[0]) + self.bound_x[0],
                         ti.random() * (self.bound_y[1] - self.bound_y[0]) + self.bound_y[0]]
            self.v[i] = [0.0, 0.0]

    @ti.kernel
    def update_grid(self):
        for i, j in self.grid_num_particles:
            self.grid_num_particles[i, j] = 0
        for i in range(self.num_particles):
            grid_idx = (self.x[i] / self.grid_size).cast(ti.i32)
            if 0 <= grid_idx.x < self.grid_res_x and 0 <= grid_idx.y < self.grid_res_y:
                cnt = ti.atomic_add(self.grid_num_particles[grid_idx], 1)
                if cnt < 60:
                    self.grid2particles[grid_idx.x, grid_idx.y, cnt] = i

    @ti.func
    def kernel(self, r):
        res = 0.0
        if 0 <= r < self.h:
            res = (1.0 - (r / self.h)**2)**3
        return res

    @ti.func
    def kernel_grad(self, r, diff):
        res = ti.Vector([0.0, 0.0])
        if 0 < r < self.h:
            g = -6.0 * (1.0 - (r / self.h)**2)**2 * (r / self.h**2)
            res = g * diff / r
        return res

    @ti.kernel
    def compute_density_pressure(self):
        for i in range(self.num_particles):
            self.rho[i] = 1e-5
            grid_idx = (self.x[i] / self.grid_size).cast(ti.i32)
            for dx, dy in ti.static(ti.ndrange((-1, 2), (-1, 2))):
                nx, ny = grid_idx.x + dx, grid_idx.y + dy
                if 0 <= nx < self.grid_res_x and 0 <= ny < self.grid_res_y:
                    for k in range(self.grid_num_particles[nx, ny]):
                        j = self.grid2particles[nx, ny, k]
                        r = (self.x[i] - self.x[j]).norm()
                        self.rho[i] += self.mass * self.kernel(r)
            self.p[i] = self.stiffness * (self.rho[i] - self.rho0)

    @ti.kernel
    def compute_forces(self, fish_pos: ti.types.ndarray(), num_fish: ti.i32, food_pos: ti.types.ndarray(), num_food: ti.i32):
        for i in range(self.num_particles):
            force = self.gravity * self.mass

            grid_idx = (self.x[i] / self.grid_size).cast(ti.i32)
            for dx, dy in ti.static(ti.ndrange((-1, 2), (-1, 2))):
                nx, ny = grid_idx.x + dx, grid_idx.y + dy
                if 0 <= nx < self.grid_res_x and 0 <= ny < self.grid_res_y:
                    for k in range(self.grid_num_particles[nx, ny]):
                        j = self.grid2particles[nx, ny, k]
                        if i == j: continue
                        diff = self.x[i] - self.x[j]
                        r = diff.norm()
                        if 0 < r < self.h:
                            # Pressure
                            force -= self.mass**2 * (self.p[i] + self.p[j]) / (2 * self.rho[j]) * self.kernel_grad(r, diff)
                            # Viscosity
                            force += self.viscosity * self.mass**2 * (self.v[j] - self.v[i]) / self.rho[j] * self.kernel(r)

            # Interaction with fish
            for f_idx in range(num_fish):
                f_p = ti.Vector([fish_pos[f_idx, 0], fish_pos[f_idx, 1]])
                diff = self.x[i] - f_p
                dist = diff.norm()
                if dist < 80.0:
                    force += diff / (dist + 0.1) * 300.0

            # Interaction with food
            for fd_idx in range(num_food):
                fd_p = ti.Vector([food_pos[fd_idx, 0], food_pos[fd_idx, 1]])
                diff = self.x[i] - fd_p
                dist = diff.norm()
                if dist < 30.0:
                    force += diff / (dist + 0.1) * 50.0

            self.v[i] += force / self.rho[i] * self.dt
            self.v[i] *= 0.98

    @ti.kernel
    def integrate(self):
        for i in range(self.num_particles):
            self.x[i] += self.v[i] * self.dt

            # Boundary
            if self.x[i].x < self.bound_x[0]:
                self.x[i].x = self.bound_x[0]; self.v[i].x *= -0.3
            if self.x[i].x > self.bound_x[1]:
                self.x[i].x = self.bound_x[1]; self.v[i].x *= -0.3
            if self.x[i].y < self.bound_y[0]:
                self.x[i].y = self.bound_y[0]; self.v[i].y *= -0.3
            if self.x[i].y > self.bound_y[1]:
                self.x[i].y = self.bound_y[1]; self.v[i].y *= -0.3

    def step(self, fishes, foods):
        f_pos = np.array([[f.x + f.size_w/2, f.y + f.size_h/2] for f in fishes], dtype=np.float32)
        if foods:
            fd_pos = np.array([[fd.x, fd.y] for fd in foods], dtype=np.float32)
        else:
            fd_pos = np.zeros((0, 2), dtype=np.float32)

        self.update_grid()
        self.compute_density_pressure()
        self.compute_forces(f_pos, len(fishes), fd_pos, len(fd_pos))
        self.integrate()

    def get_positions(self):
        return self.x.to_numpy()
