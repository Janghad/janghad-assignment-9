import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.animation import FuncAnimation
import os
from functools import partial
from matplotlib.patches import Circle

result_dir = "results"
os.makedirs(result_dir, exist_ok=True)

# Define a simple MLP class
class MLP:
    def __init__(self, input_dim, hidden_dim, output_dim, lr, activation='tanh'):
        np.random.seed(0)
        self.lr = lr # learning rate
        self.activation_fn = activation # activation function
        # TODO: define layers and initialize weights
        self.W1 = np.random.randn(input_dim, hidden_dim) * 0.01
        self.b1 = np.zeros((1, hidden_dim))
        self.W2 = np.random.randn(hidden_dim, output_dim) * 0.01
        self.b2 = np.zeros((1, output_dim))

    def forward(self, X):
        # TODO: forward pass, apply layers to input X
        self.X = X
        self.Z1 = np.dot(X, self.W1) + self.b1
        if self.activation_fn == 'tanh':
            self.A1 = np.tanh(self.Z1)
        elif self.activation_fn == 'relu':
            self.A1 = np.maximum(0, self.Z1)
        elif self.activation_fn == 'sigmoid':
            self.A1 = 1 / (1 + np.exp(-self.Z1))
        else:
            raise ValueError("Invalid activation function")
        self.Z2 = np.dot(self.A1, self.W2) + self.b2
        self.out = 1 / (1 + np.exp(-self.Z2))  # Sigmoid activation for output layer
        # TODO: store activations for visualization
        return self.out

    def backward(self, X, y):
        # TODO: compute gradients using chain rule
        m = X.shape[0]
        dZ2 = self.out - y
        dW2 = (1 / m) * np.dot(self.A1.T, dZ2)
        db2 = (1 / m) * np.sum(dZ2, axis=0, keepdims=True)
        if self.activation_fn == 'tanh':
            dA1 = np.dot(dZ2, self.W2.T) * (1 - np.tanh(self.Z1) ** 2)
        elif self.activation_fn == 'relu':
            dA1 = np.dot(dZ2, self.W2.T)
            dA1[self.Z1 <= 0] = 0
        elif self.activation_fn == 'sigmoid':
            sig = 1 / (1 + np.exp(-self.Z1))
            dA1 = np.dot(dZ2, self.W2.T) * sig * (1 - sig)
        dW1 = (1 / m) * np.dot(X.T, dA1)
        db1 = (1 / m) * np.sum(dA1, axis=0, keepdims=True)

        # TODO: update weights with gradient descent
        self.W2 -= self.lr * dW2
        self.b2 -= self.lr * db2
        self.W1 -= self.lr * dW1
        self.b1 -= self.lr * db1
        # TODO: store gradients for visualization
        self.dW1 = dW1
        self.dW2 = dW2
        pass

def generate_data(n_samples=100):
    np.random.seed(0)
    # Generate input
    X = np.random.randn(n_samples, 2)
    y = (X[:, 0] ** 2 + X[:, 1] ** 2 > 1).astype(int) * 2 - 1  # Circular boundary
    y = y.reshape(-1, 1)
    return X, y

# Visualization update function
def update(frame, mlp, ax_input, ax_hidden, ax_gradient, X, y):
    ax_hidden.clear()
    ax_input.clear()
    ax_gradient.clear()

    # Perform training steps
    for _ in range(10):
        mlp.forward(X)
        mlp.backward(X, y)

    # TODO: Plot hidden features
    hidden_features = mlp.A1  # Hidden layer activations
    ax_hidden.scatter(
        hidden_features[:, 0],
        hidden_features[:, 1],
        hidden_features[:, 2],
        c=y.ravel(),
        cmap='bwr',
        alpha=0.7
    )
    ax_hidden.set_title(f"Hidden Space at Step {frame * 10}")
    ax_hidden.set_xlabel("Neuron 1 Activation")
    ax_hidden.set_ylabel("Neuron 2 Activation")
    ax_hidden.set_zlabel("Neuron 3 Activation")

    # TODO: Hyperplane visualization in the hidden space
    W2_flat = mlp.W2.flatten()
    b2_scalar = mlp.b2.flatten()[0]
    if np.linalg.norm(W2_flat) > 1e-6:
        x_range = np.linspace(hidden_features[:, 0].min(), hidden_features[:, 0].max(), 10)
        y_range = np.linspace(hidden_features[:, 1].min(), hidden_features[:, 1].max(), 10)
        X_grid, Y_grid = np.meshgrid(x_range, y_range)
        Z_grid = (-W2_flat[0] * X_grid - W2_flat[1] * Y_grid - b2_scalar) / (W2_flat[2] + 1e-6)
        ax_hidden.plot_surface(X_grid, Y_grid, Z_grid, alpha=0.3, color='yellow')
    else:
        pass  # Skip if the hyperplane cannot be computed

    # TODO: Distorted input space transformed by the hidden layer
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    grid_resolution = 30
    xx, yy = np.meshgrid(
        np.linspace(x_min, x_max, grid_resolution),
        np.linspace(y_min, y_max, grid_resolution)
    )
    grid_points = np.c_[xx.ravel(), yy.ravel()]
    Z1_grid = np.dot(grid_points, mlp.W1) + mlp.b1
    if mlp.activation_fn == 'tanh':
        A1_grid = np.tanh(Z1_grid)
    elif mlp.activation_fn == 'relu':
        A1_grid = np.maximum(0, Z1_grid)
    elif mlp.activation_fn == 'sigmoid':
        A1_grid = 1 / (1 + np.exp(-Z1_grid))
    else:
        raise ValueError("Invalid activation function")
    A1_grid_x = A1_grid[:, 0].reshape(xx.shape)
    A1_grid_y = A1_grid[:, 1].reshape(xx.shape)
    for i in range(grid_resolution):
        ax_gradient.plot(
            A1_grid_x[i, :],
            A1_grid_y[i, :],
            color='lightgray',
            linewidth=0.5
        )
    for j in range(grid_resolution):
        ax_gradient.plot(
            A1_grid_x[:, j],
            A1_grid_y[:, j],
            color='lightgray',
            linewidth=0.5
        )
    hidden_features_2d = hidden_features[:, :2]
    ax_gradient.scatter(
        hidden_features_2d[:, 0],
        hidden_features_2d[:, 1],
        c=y.ravel(),
        cmap='bwr',
        edgecolors='k',
        alpha=0.7
    )
    ax_gradient.set_title(f"Distorted Input Space at Step {frame * 10}")
    ax_gradient.set_xlabel("Activation of Neuron 1")
    ax_gradient.set_ylabel("Activation of Neuron 2")

    # TODO: Plot input layer decision boundary

    Z = mlp.forward(grid_points).reshape(xx.shape)  # Evaluate the model on the grid
    ax_input.contourf(
        xx,
        yy,
        Z,
        levels=[0, 0.5, 1],
        alpha=0.3,
        colors=['blue', 'red']  # Blue and red for decision regions
    )
    # Plot the training data points
    ax_input.scatter(
        X[:, 0],
        X[:, 1],
        c=y.ravel(),
        cmap='bwr',  # Color based on class label
        edgecolors='k',  # Black edges for points
        alpha=0.7  # Ensure visibility
    )
    # Set titles and labels
    ax_input.set_title(f"Input Space at Step {frame * 10}")
    ax_input.set_xlabel("X1")
    ax_input.set_ylabel("X2")


    # TODO: Visualize features and gradients as circles and edges
    ax_gradient.set_xlim(0, 1)
    ax_gradient.set_ylim(0, 1)
    ax_gradient.axis("off")

    # Draw nodes
    input_positions = [(0.2, 0.1), (0.2, 0.9)]
    hidden_positions = [(0.5, 0.2), (0.5, 0.5), (0.5, 0.8)]
    output_position = [(0.8, 0.5)]
    node_positions = input_positions + hidden_positions + output_position
    node_labels = ["x1", "x2", "h1", "h2", "h3", "y"]

    for pos, label in zip(node_positions, node_labels):
        ax_gradient.add_patch(Circle(pos, 0.05, color="blue", alpha=0.8))
        ax_gradient.text(pos[0], pos[1] + 0.06, label, ha="center", va="center", fontsize=8)

    # Draw edges with consistent thickness
    connections = [
        (input_positions[0], hidden_positions[0]),
        (input_positions[0], hidden_positions[1]),
        (input_positions[0], hidden_positions[2]),
        (input_positions[1], hidden_positions[0]),
        (input_positions[1], hidden_positions[1]),
        (input_positions[1], hidden_positions[2]),
        (hidden_positions[0], output_position[0]),
        (hidden_positions[1], output_position[0]),
        (hidden_positions[2], output_position[0]),
    ]

    # Compute gradients and normalize
    gradients = np.concatenate([mlp.dW1.flatten(), mlp.dW2.flatten()])
    max_gradient = max(1e-6, gradients.max())  # Avoid division by zero
    normalized_gradients = gradients / max_gradient

    # Plot edges with thickness based on gradient magnitude
    for (start, end), grad in zip(connections, normalized_gradients):
        ax_gradient.plot(
            [start[0], end[0]],
            [start[1], end[1]],
            color="purple",
            alpha=0.5,
            linewidth=1 + 5 * grad  # Scaled thickness
        )

    ax_gradient.set_title(f"Gradients at Step {frame * 10}")



def visualize(activation, lr, step_num):
    X, y = generate_data()
    mlp = MLP(input_dim=2, hidden_dim=3, output_dim=1, lr=lr, activation=activation)

    # Set up visualization
    matplotlib.use('agg')
    fig = plt.figure(figsize=(21, 7))
    ax_hidden = fig.add_subplot(131, projection='3d')
    ax_input = fig.add_subplot(132)
    ax_gradient = fig.add_subplot(133)

    # Create animation
    ani = FuncAnimation(fig, partial(update, mlp=mlp, ax_input=ax_input, ax_hidden=ax_hidden, ax_gradient=ax_gradient, X=X, y=y), frames=step_num//10, repeat=False)

    # Save the animation as a GIF
    ani.save(os.path.join(result_dir, "visualize.gif"), writer='pillow', fps=10)
    plt.close()

if __name__ == "__main__":
    activation = "tanh"
    lr = 0.1
    step_num = 1000
    visualize(activation, lr, step_num)