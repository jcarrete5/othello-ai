#include "board.h"
#include "aimax.h"

#include <pybind11/pybind11.h>

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

namespace py = pybind11;

PYBIND11_MODULE(othello_cpp, m) {
  m.doc() = R"pbdoc(
        .. currentmodule:: othello_cpp

        .. autosummary::
           :toctree: _generate

    )pbdoc";

  py::enum_<othello::Color>(m, "Color")
      .value("NONE", othello::Color::NONE)
      .value("BLACK", othello::Color::BLACK)
      .value("WHITE", othello::Color::WHITE)
      .value("MAX_COLOR", othello::Color::MAX_COLOR)
      .export_values();

  py::class_<othello::Position>(m, "Position")
      .def(py::init<size_t, size_t>())
      .def_readwrite("row", &othello::Position::row)
      .def_readwrite("col", &othello::Position::col);

  py::class_<othello::GameBoard>(m, "GameBoard")
      .def(py::init())
      .def("set_up", &othello::GameBoard::set_up)
      .def("at", &othello::GameBoard::at)
      .def("set", &othello::GameBoard::set)
      .def("vacant", &othello::GameBoard::vacant)
      .def("valid_moves", &othello::GameBoard::valid_moves)
      .def("place_piece", &othello::GameBoard::place_piece);

  m.def("AIMax_best_move", &othello::AIMax::best_move);

#ifdef VERSION_INFO
  m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
  m.attr("__version__") = "dev";
#endif

}
