@init
    SET A #0
    SET B #0b11111101
    SET_ZERO C

@test_val
    STORE B [A]
    LOAD [A] ACC
    JUMP_IF_EQ_ACC B @next_val
    HALT

@next_val
    INCR B
    JUMP_IF_NOT_OVERFLOW_FLAG @test_val
    INCR A
    JUMP_IF_NOT_OVERFLOW_FLAG @test_val
    INCR C
    JUMP @test_val