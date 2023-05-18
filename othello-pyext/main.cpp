#include "aimax.h"
#include "board.h"

#include <pybind11/pybind11.h>

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

namespace py = pybind11;
using namespace othello;

using PositionIntConst = int (Position::*)() const;
using PositionIntRef = int &(Position::*)();

PYBIND11_MODULE(othello_cpp, m) {
  m.doc() = R"pbdoc(
        .. currentmodule:: othello_cpp

        .. autosummary::
           :toctree: _generate
    )pbdoc";

  py::enum_<Color>(m, "Color")
      .value("Black", Color::black)
      .value("White", Color::white)
      .export_values();

  py::class_<Position>(m, "Position")
      .def(py::init<int, int>())
      .def_property("row", static_cast<PositionIntConst>(&Position::x),
                    static_cast<PositionIntRef>(&Position::x))
      .def_property("col", static_cast<PositionIntConst>(&Position::y),
                    static_cast<PositionIntRef>(&Position::y));

  py::class_<GameBoard>(m, "GameBoard")
      .def(py::init())
      .def("at", &GameBoard::at)
      .def("set", &GameBoard::set_position)
      .def("clear", &GameBoard::clear_position)
      .def("clear_all", &GameBoard::clear_all)
      .def("white_positions", &GameBoard::white_positions)
      .def("black_positions", &GameBoard::black_positions)
      .def("__repr__", &GameBoard::to_string);

  py::class_<Game>(m, "Game")
      .def(py::init())
      .def(py::init<GameBoard, Color>())
      .def_property_readonly("board", &Game::board)
      .def("valid_moves", &Game::valid_moves)
      .def("is_valid_move", &Game::is_valid_move)
      .def("place_piece", &Game::place_piece)
      .def("is_game_over", &Game::is_game_over)
      .def("reset", &Game::reset);

  m.def("AIMax_best_move", &ai_max::best_move,
        py::call_guard<py::gil_scoped_release>());

#ifdef VERSION_INFO
  m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
  m.attr("__version__") = "dev";
#endif
}
